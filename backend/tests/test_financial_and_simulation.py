"""Unit and integration tests for Financial Analysis Service and Monte Carlo Simulation."""

import pytest
from fastapi.testclient import TestClient

from app.services.financial_service import FinancialService
from app.services.simulation_service import MonteCarloSimulator
from tests.test_analyses_validation import make_valid_payload


# 1. Deterministic Financial Service Tests
def test_financial_service_profitable_scenario():
    """Verify revenue, expenses, profit, and break-even calculations for a profitable business."""
    # spend=300, customers=100, days=30 -> Revenue = 900,000
    # Fixed = Rent(50k) + Salaries(80k) + Utilities(15k) + Other(20k) = 165,000
    # Variable = COGS(200k)
    # Total Expenses = 365,000
    # Operating Profit = 900,000 - 365,000 = 535,000
    res = FinancialService.calculate(
        initial_investment=1000000.0,
        working_capital=300000.0,
        average_customer_spend=300.0,
        expected_customers_per_day=100,
        operating_days_per_month=30,
        rent_per_month=50000.0,
        salaries_per_month=80000.0,
        inventory_or_cogs_per_month=200000.0,
        utilities_per_month=15000.0,
        other_expenses_per_month=20000.0,
        period_months=12,
    )

    assert res.monthly_revenue == 900000.0
    assert res.fixed_monthly_expenses == 165000.0
    assert res.variable_monthly_expenses == 200000.0
    assert res.total_monthly_expenses == 365000.0
    assert res.monthly_operating_profit == 535000.0
    assert res.operating_margin_percentage == 59.44
    assert res.is_operationally_profitable is True
    assert res.cash_shortfall is False
    assert res.shortfall_amount == 0.0

    # Payback: 1,000,000 / 535,000 = 1.86 -> Month 2
    assert res.payback_period_months == 2

    # Break-even check
    assert res.break_even_monthly_revenue is not None
    assert res.break_even_monthly_revenue < res.monthly_revenue
    assert res.break_even_daily_customers is not None
    assert res.break_even_daily_customers < 100

    # Cash flow trajectory
    assert len(res.cash_flow_trajectory) == 12
    assert res.cash_flow_trajectory[0].month == 1
    assert res.cash_flow_trajectory[0].starting_cash == 300000.0
    assert res.cash_flow_trajectory[0].ending_cash == 300000.0 + 535000.0
    assert res.cash_flow_trajectory[-1].month == 12


def test_financial_service_unprofitable_cash_shortfall():
    """Verify loss-making scenario detects negative cash flow and shortfall deficit."""
    # Low footfall: spend=100, customers=20, days=30 -> Revenue = 60,000
    # Fixed costs = 120,000, COGS = 30,000 -> Total = 150,000
    # Loss = -90,000 per month
    # Working capital = 100,000 (exhausted by Month 2)
    res = FinancialService.calculate(
        initial_investment=500000.0,
        working_capital=100000.0,
        average_customer_spend=100.0,
        expected_customers_per_day=20,
        operating_days_per_month=30,
        rent_per_month=40000.0,
        salaries_per_month=60000.0,
        inventory_or_cogs_per_month=30000.0,
        utilities_per_month=10000.0,
        other_expenses_per_month=10000.0,
        period_months=6,
    )

    assert res.monthly_revenue == 60000.0
    assert res.monthly_operating_profit == -90000.0
    assert res.is_operationally_profitable is False
    assert res.cash_shortfall is True
    assert res.shortfall_amount > 0.0
    assert res.month_of_minimum_cash == 6
    assert res.payback_period_months is None


# 2. Monte Carlo Stochastic Simulation Tests
def test_monte_carlo_simulator_distributions():
    """Verify stochastic percentile progression and reproducibility with fixed seed."""
    sim = MonteCarloSimulator()
    result1 = sim.run_simulation(
        average_customer_spend=250.0,
        expected_customers_per_day=80,
        operating_days_per_month=30,
        fixed_expenses=150000.0,
        variable_cogs=120000.0,
        initial_investment=800000.0,
        simulation_count=1000,
        seed=42,
    )

    result2 = sim.run_simulation(
        average_customer_spend=250.0,
        expected_customers_per_day=80,
        operating_days_per_month=30,
        fixed_expenses=150000.0,
        variable_cogs=120000.0,
        initial_investment=800000.0,
        simulation_count=1000,
        seed=42,
    )

    # Deterministic reproducibility
    assert result1.scenarios[0].monthly_revenue == result2.scenarios[0].monthly_revenue
    assert result1.risk_metrics.probability_of_profit == result2.risk_metrics.probability_of_profit

    # Percentile ordering: P10 (conservative) <= P50 (base) <= P90 (aggressive)
    p10 = result1.scenarios[0]
    p50 = result1.scenarios[1]
    p90 = result1.scenarios[2]

    assert p10.scenario == "conservative"
    assert p50.scenario == "base"
    assert p90.scenario == "aggressive"

    assert p10.monthly_revenue <= p50.monthly_revenue <= p90.monthly_revenue
    assert p10.monthly_operating_profit <= p50.monthly_operating_profit <= p90.monthly_operating_profit

    # Risk metrics validation
    assert 0.0 <= result1.risk_metrics.probability_of_profit <= 1.0
    assert len(result1.disclosures) >= 3


# 3. End-to-End Pipeline Execution Endpoint Tests
def test_execute_analysis_pipeline_success(client: TestClient):
    """POST /api/analyses/{id}/execute transitions PENDING to COMPLETED and stores results."""
    payload = make_valid_payload()
    create_res = client.post("/api/analyses", json=payload)
    assert create_res.status_code == 201
    analysis_id = create_res.json()["id"]

    # Execute simulation pipeline
    exec_res = client.post(f"/api/analyses/{analysis_id}/execute")
    assert exec_res.status_code == 200

    data = exec_res.json()
    assert data["id"] == analysis_id
    assert data["status"] == "COMPLETED"
    assert data["results"] is not None

    res_body = data["results"]
    assert "financial_projections" in res_body
    assert "simulation" in res_body
    assert "recommendations" in res_body
    assert "data_quality" in res_body
    assert len(res_body["recommendations"]) > 0

    # Subsequent GET /api/analyses/{id} should return COMPLETED with populated results
    detail_res = client.get(f"/api/analyses/{analysis_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["status"] == "COMPLETED"
    assert detail["results"]["financial_projections"]["monthly_revenue"] > 0


def test_execute_analysis_not_found(client: TestClient):
    """POST /api/analyses/{id}/execute with invalid UUID returns 404."""
    unknown_id = "00000000-0000-0000-0000-000000000000"
    res = client.post(f"/api/analyses/{unknown_id}/execute")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"
