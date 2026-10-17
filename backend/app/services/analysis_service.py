"""Analysis Pipeline Coordinator orchestrating financial, location, and simulation pipelines."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.analysis import AnalysisRecord, AnalysisStatus
from app.services.financial_service import FinancialService
from app.services.simulation_service import MonteCarloSimulator

logger = logging.getLogger("biztwin.analysis_service")


class AnalysisPipelineService:
    """Coordinates feasibility modeling and persists computed outputs into AnalysisRecord."""

    @classmethod
    def execute_analysis(cls, analysis_id: str, db: Optional[Session] = None) -> None:
        """Synchronously or background-executed pipeline running full feasibility modeling."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        try:
            record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
            if not record:
                logger.error("Analysis pipeline could not find record with ID %s", analysis_id)
                return

            # Mark status as PROCESSING
            record.status = AnalysisStatus.PROCESSING.value
            record.updated_at = datetime.now(timezone.utc)
            db.commit()

            raw_input = record.input_data or {}
            biz_in = raw_input.get("business", {})
            loc_in = raw_input.get("location", {})
            fin_in = raw_input.get("financial", {})
            proj_in = raw_input.get("projection", {})

            # 1. Deterministic Financial Projections
            fin_result = FinancialService.calculate(
                initial_investment=float(fin_in.get("initial_investment", 0.0)),
                working_capital=float(fin_in.get("working_capital", 0.0)),
                average_customer_spend=float(fin_in.get("average_customer_spend", 100.0)),
                expected_customers_per_day=int(fin_in.get("expected_customers_per_day", 50)),
                operating_days_per_month=int(fin_in.get("operating_days_per_month", 30)),
                rent_per_month=float(fin_in.get("rent_per_month", 0.0)),
                salaries_per_month=float(fin_in.get("salaries_per_month", 0.0)),
                inventory_or_cogs_per_month=float(fin_in.get("inventory_or_cogs_per_month", 0.0)),
                utilities_per_month=float(fin_in.get("utilities_per_month", 0.0)),
                other_expenses_per_month=float(fin_in.get("other_expenses_per_month", 0.0)),
                period_months=int(proj_in.get("period_months", 12)),
                currency=str(fin_in.get("currency", "INR")),
            )

            # 2. Monte Carlo Stochastic Simulation
            sim_count = int(proj_in.get("simulation_count", 1000))
            simulator = MonteCarloSimulator()
            sim_result = simulator.run_simulation(
                average_customer_spend=float(fin_in.get("average_customer_spend", 100.0)),
                expected_customers_per_day=int(fin_in.get("expected_customers_per_day", 50)),
                operating_days_per_month=int(fin_in.get("operating_days_per_month", 30)),
                fixed_expenses=fin_result.fixed_monthly_expenses,
                variable_cogs=fin_result.variable_monthly_expenses,
                initial_investment=fin_result.initial_investment,
                simulation_count=sim_count,
            )

            # 3. Grounded Business Recommendations
            recommendations: List[str] = []
            if fin_result.is_operationally_profitable:
                recommendations.append(
                    f"Baseline operations are profitable with an estimated monthly operating profit of ₹{fin_result.monthly_operating_profit:,.2f} ({fin_result.operating_margin_percentage}% margin)."
                )
            else:
                recommendations.append(
                    f"Baseline monthly operations operate at a loss of ₹{abs(fin_result.monthly_operating_profit):,.2f}. Review fixed lease expenses or increase ticket size."
                )

            if fin_result.break_even_daily_customers is not None:
                recommendations.append(
                    f"Target daily footfall threshold to break even is {fin_result.break_even_daily_customers:.0f} customers per day (currently modeled at {fin_in.get('expected_customers_per_day')})."
                )

            if fin_result.cash_shortfall:
                recommendations.append(
                    f"Liquidity risk detected: projected cash balance falls into a deficit of ₹{fin_result.shortfall_amount:,.2f} at month {fin_result.month_of_minimum_cash}. Additional working capital is advised."
                )
            else:
                recommendations.append(
                    f"Working capital buffer of ₹{fin_result.working_capital:,.2f} sustains operations throughout the {proj_in.get('period_months', 12)}-month horizon."
                )

            if fin_result.payback_period_months:
                recommendations.append(
                    f"Initial capital expenditure of ₹{fin_result.initial_investment:,.2f} is estimated to be recovered by month {fin_result.payback_period_months}."
                )
            else:
                recommendations.append(
                    f"Initial capital expenditure is not fully recouped within the initial {proj_in.get('period_months', 12)}-month projection horizon."
                )

            # 4. Location Context
            location_summary = {
                "address": loc_in.get("address", record.address),
                "latitude": loc_in.get("latitude", record.latitude),
                "longitude": loc_in.get("longitude", record.longitude),
                "radius_meters": loc_in.get("radius_meters", record.radius_meters),
                "target_category": biz_in.get("category", record.business_category),
            }

            # 5. Data Quality and Provenance
            has_history = bool(biz_in.get("historical_data_id"))
            data_quality = {
                "business_mode": record.business_mode,
                "has_verified_historical_records": has_history,
                "confidence_level": "MODERATE_HISTORICAL" if has_history else "BASELINE_ASSUMPTIONS",
                "notes": (
                    "Projections utilize user-declared assumptions and stochastic volatility curves. "
                    "Verified historical financial upload was attached."
                    if has_history
                    else "Projections rely entirely on user baseline assumptions without audited prior accounting records."
                ),
            }

            # Assemble complete results JSON
            results_payload = {
                "financial_projections": fin_result.model_dump(),
                "simulation": sim_result.model_dump(),
                "location_summary": location_summary,
                "recommendations": recommendations,
                "data_quality": data_quality,
                "limitations": fin_result.limitations + sim_result.disclosures,
            }

            # Update record to COMPLETED
            record.status = AnalysisStatus.COMPLETED.value
            record.results_data = results_payload
            record.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info("Analysis pipeline COMPLETED successfully for id=%s", analysis_id)

        except Exception as e:
            db.rollback()
            logger.exception("Analysis pipeline failed for id=%s: %s", analysis_id, e)
            try:
                record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
                if record:
                    record.status = AnalysisStatus.FAILED.value
                    record.error_message = f"Analysis computation failed: {str(e)}"
                    record.updated_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception as inner_e:
                logger.error("Failed to mark analysis as FAILED: %s", inner_e)
        finally:
            if should_close:
                db.close()
