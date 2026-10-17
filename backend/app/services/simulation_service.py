"""AI/ML and Monte Carlo Simulation Integration Boundary."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger("biztwin.simulation_service")


class ScenarioMetrics(BaseModel):
    """Feasibility outcome for a specific scenario percentile."""

    scenario: str = Field(..., description="Scenario identifier ('conservative', 'base', 'aggressive')")
    percentile: int = Field(..., description="Distribution percentile (e.g., 10, 50, 90)")
    monthly_revenue: float = Field(..., description="Projected monthly revenue in this scenario")
    monthly_operating_profit: float = Field(..., description="Projected monthly operating profit in this scenario")
    operating_margin_pct: float = Field(..., description="Operating margin percentage in this scenario")
    estimated_payback_months: Optional[int] = Field(
        default=None, description="Months to recoup CapEx in this scenario"
    )


class RiskMetrics(BaseModel):
    """Risk indicators derived from stochastic distribution modeling."""

    probability_of_profit: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Conditional probability that operating income is positive (0.0 to 1.0)",
    )
    worst_case_monthly_profit_p5: float = Field(
        ..., description="5th percentile monthly profit (Value at Risk threshold)"
    )
    expected_value_profit: float = Field(..., description="Mean monthly operating profit across all iterations")
    profit_volatility_std: float = Field(..., description="Standard deviation of monthly operating profit")


class SimulationMetadata(BaseModel):
    """Audit metadata describing simulation provenance and parameters."""

    model_name: str = Field(..., description="Model identifier")
    model_version: str = Field(..., description="Semantic version of simulation engine")
    simulation_count: int = Field(..., description="Total executed simulation iterations")
    seed: int = Field(..., description="Pseudo-random generator seed for reproducibility")
    distributions: Dict[str, str] = Field(..., description="Documented statistical distributions")


class SimulationResult(BaseModel):
    """Complete structured output from the simulation integration boundary."""

    status: str = Field(default="COMPLETED", description="Simulation status ('COMPLETED', 'UNAVAILABLE')")
    metadata: SimulationMetadata
    scenarios: List[ScenarioMetrics] = Field(..., description="Conservative, Base, and Aggressive scenario outcomes")
    risk_metrics: RiskMetrics
    disclosures: List[str] = Field(..., description="Mandatory methodology and assumption disclosures")


class BaseSimulationProvider(ABC):
    """Abstract interface for AI/ML and stochastic simulation engines."""

    @abstractmethod
    def run_simulation(
        self,
        average_customer_spend: float,
        expected_customers_per_day: int,
        operating_days_per_month: int,
        fixed_expenses: float,
        variable_cogs: float,
        initial_investment: float,
        simulation_count: int = 1000,
        seed: Optional[int] = 42,
    ) -> SimulationResult:
        """Execute simulation run and return normalized scenario distributions."""
        pass


class MonteCarloSimulator(BaseSimulationProvider):
    """Deterministic Monte Carlo engine simulating stochastic revenue and cost volatility."""

    def run_simulation(
        self,
        average_customer_spend: float,
        expected_customers_per_day: int,
        operating_days_per_month: int,
        fixed_expenses: float,
        variable_cogs: float,
        initial_investment: float,
        simulation_count: int = 1000,
        seed: Optional[int] = 42,
    ) -> SimulationResult:
        """Run vectorized Monte Carlo simulation with documented statistical distributions."""
        rng = np.random.default_rng(seed)

        # 1. Stochastic Customer Footfall (Normal distribution, 15% volatility, non-negative)
        cust_std = max(1.0, expected_customers_per_day * 0.15)
        sim_customers = np.maximum(0, rng.normal(expected_customers_per_day, cust_std, simulation_count))

        # 2. Stochastic Customer Spend (Normal distribution, 10% volatility, minimum ₹1.0)
        spend_std = max(0.5, average_customer_spend * 0.10)
        sim_spend = np.maximum(1.0, rng.normal(average_customer_spend, spend_std, simulation_count))

        # 3. Stochastic COGS variation (Uniform ±5%)
        cogs_mult = rng.uniform(0.95, 1.05, simulation_count)
        sim_cogs = variable_cogs * cogs_mult

        # 4. Stochastic Overhead variation (Normal ±3%)
        overhead_mult = np.maximum(0.90, rng.normal(1.0, 0.03, simulation_count))
        sim_fixed = fixed_expenses * overhead_mult

        # 5. Vectorized Revenue and Profit calculations
        sim_monthly_revenue = sim_customers * sim_spend * operating_days_per_month
        sim_total_expenses = sim_fixed + sim_cogs
        sim_profits = sim_monthly_revenue - sim_total_expenses

        # Percentile outcomes
        p10_rev = float(np.percentile(sim_monthly_revenue, 10))
        p10_profit = float(np.percentile(sim_profits, 10))
        p10_margin = round((p10_profit / p10_rev) * 100.0, 2) if p10_rev > 0 else 0.0

        p50_rev = float(np.percentile(sim_monthly_revenue, 50))
        p50_profit = float(np.percentile(sim_profits, 50))
        p50_margin = round((p50_profit / p50_rev) * 100.0, 2) if p50_rev > 0 else 0.0

        p90_rev = float(np.percentile(sim_monthly_revenue, 90))
        p90_profit = float(np.percentile(sim_profits, 90))
        p90_margin = round((p90_profit / p90_rev) * 100.0, 2) if p90_rev > 0 else 0.0

        def calc_payback(profit: float) -> Optional[int]:
            if profit <= 0:
                return None
            months = int(np.ceil(initial_investment / profit))
            return months if months <= 60 else None

        scenarios = [
            ScenarioMetrics(
                scenario="conservative",
                percentile=10,
                monthly_revenue=round(p10_rev, 2),
                monthly_operating_profit=round(p10_profit, 2),
                operating_margin_pct=p10_margin,
                estimated_payback_months=calc_payback(p10_profit),
            ),
            ScenarioMetrics(
                scenario="base",
                percentile=50,
                monthly_revenue=round(p50_rev, 2),
                monthly_operating_profit=round(p50_profit, 2),
                operating_margin_pct=p50_margin,
                estimated_payback_months=calc_payback(p50_profit),
            ),
            ScenarioMetrics(
                scenario="aggressive",
                percentile=90,
                monthly_revenue=round(p90_rev, 2),
                monthly_operating_profit=round(p90_profit, 2),
                operating_margin_pct=p90_margin,
                estimated_payback_months=calc_payback(p90_profit),
            ),
        ]

        # Risk metrics
        prob_profit = float(np.mean(sim_profits > 0))
        p5_worst = float(np.percentile(sim_profits, 5))
        mean_profit = float(np.mean(sim_profits))
        std_profit = float(np.std(sim_profits))

        risk_metrics = RiskMetrics(
            probability_of_profit=round(prob_profit, 3),
            worst_case_monthly_profit_p5=round(p5_worst, 2),
            expected_value_profit=round(mean_profit, 2),
            profit_volatility_std=round(std_profit, 2),
        )

        metadata = SimulationMetadata(
            model_name="BizTwin-MonteCarlo-Stochastic",
            model_version="1.0.0",
            simulation_count=simulation_count,
            seed=seed or 42,
            distributions={
                "daily_footfall": f"Normal(mean={expected_customers_per_day}, std={cust_std:.1f}, min=0)",
                "customer_spend": f"Normal(mean={average_customer_spend}, std={spend_std:.1f}, min=1.0)",
                "cogs": "Uniform(0.95, 1.05) multiplier",
                "fixed_expenses": "Normal(mean=1.0, std=0.03) multiplier",
            },
        )

        disclosures = [
            "Simulated probabilities and percentiles are conditional upon user-defined parameter distributions and assumptions.",
            "Monte Carlo outputs do not represent observed empirical business outcomes or market guarantees.",
            "AI/ML supervised model integration boundary remains ready for empirical regional training data from team AI/ML engineer.",
        ]

        return SimulationResult(
            status="COMPLETED",
            metadata=metadata,
            scenarios=scenarios,
            risk_metrics=risk_metrics,
            disclosures=disclosures,
        )
