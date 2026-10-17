"""Deterministic Financial Analysis Service for BizTwin Feasibility Projections."""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("biztwin.financial_service")


class MonthlyCashFlowPoint(BaseModel):
    """Monthly cash trajectory snapshot suitable for frontend charts."""

    month: int = Field(..., description="Projection month index (1 to N)")
    starting_cash: float = Field(..., description="Cash liquidity at start of period (INR)")
    revenue: float = Field(..., description="Projected monthly gross revenue (INR)")
    operating_expenses: float = Field(..., description="Total monthly operational costs (INR)")
    operating_profit: float = Field(..., description="Monthly operating income / EBITDA (INR)")
    ending_cash: float = Field(..., description="Cash liquidity at end of period (INR)")
    cumulative_net_profit: float = Field(..., description="Cumulative retained earnings (INR)")


class FinancialAnalysisResult(BaseModel):
    """Comprehensive output of deterministic financial feasibility calculations."""

    currency: str = Field(default="INR", description="Applied currency")
    initial_investment: float = Field(..., description="Initial CapEx startup expenditure")
    working_capital: float = Field(..., description="Initial liquidity reserve")
    monthly_revenue: float = Field(..., description="Baseline estimated monthly revenue")
    fixed_monthly_expenses: float = Field(..., description="Total fixed monthly operating costs")
    variable_monthly_expenses: float = Field(..., description="Total variable costs (COGS / inventory)")
    total_monthly_expenses: float = Field(..., description="Total monthly recurring expenses")
    monthly_operating_profit: float = Field(..., description="Monthly operating income (EBITDA)")
    operating_margin_percentage: float = Field(..., description="Operating margin percentage")
    break_even_monthly_revenue: Optional[float] = Field(
        default=None, description="Revenue required to cover all operating costs"
    )
    break_even_daily_customers: Optional[float] = Field(
        default=None, description="Daily customer footfall needed to achieve break-even"
    )
    is_operationally_profitable: bool = Field(..., description="True if monthly operating profit > 0")
    payback_period_months: Optional[int] = Field(
        default=None, description="Estimated months to recoup initial CapEx, or None if unrecovered"
    )
    minimum_cash_balance: float = Field(..., description="Lowest cash balance reached during projection horizon")
    month_of_minimum_cash: int = Field(..., description="Month when lowest cash point occurs")
    cash_shortfall: bool = Field(..., description="True if cash balance ever dips below zero")
    shortfall_amount: float = Field(..., description="Capital shortfall amount needed to avoid insolvency (INR)")
    cash_flow_trajectory: List[MonthlyCashFlowPoint] = Field(
        default_factory=list, description="Ordered monthly cash progression data points"
    )
    assumptions: List[str] = Field(default_factory=list, description="Documented baseline assumptions")
    limitations: List[str] = Field(default_factory=list, description="Model boundary exclusions and disclosures")


class FinancialService:
    """Calculates deterministic feasibility projections, break-even targets, and cash runways."""

    @classmethod
    def calculate(
        cls,
        initial_investment: float,
        working_capital: float,
        average_customer_spend: float,
        expected_customers_per_day: int,
        operating_days_per_month: int,
        rent_per_month: float,
        salaries_per_month: float,
        inventory_or_cogs_per_month: float,
        utilities_per_month: float,
        other_expenses_per_month: float,
        period_months: int = 12,
        currency: str = "INR",
    ) -> FinancialAnalysisResult:
        """Execute deterministic financial calculations based on validated user parameters."""
        # 1. Revenue estimation based on footfall and spend assumptions
        monthly_revenue = round(
            average_customer_spend * expected_customers_per_day * operating_days_per_month,
            2,
        )

        # 2. Expense classification
        fixed_expenses = round(
            rent_per_month + salaries_per_month + utilities_per_month + other_expenses_per_month,
            2,
        )
        variable_expenses = round(inventory_or_cogs_per_month, 2)
        total_expenses = round(fixed_expenses + variable_expenses, 2)

        # 3. Operating profit & margin
        operating_profit = round(monthly_revenue - total_expenses, 2)
        margin_pct = (
            round((operating_profit / monthly_revenue) * 100.0, 2)
            if monthly_revenue > 0
            else 0.0
        )

        # 4. Break-even analysis
        break_even_revenue = None
        break_even_customers = None

        if monthly_revenue > 0:
            variable_ratio = variable_expenses / monthly_revenue
            if variable_ratio < 1.0:
                break_even_revenue = round(fixed_expenses / (1.0 - variable_ratio), 2)
                spend_per_day_unit = average_customer_spend * operating_days_per_month
                if spend_per_day_unit > 0:
                    break_even_customers = round(break_even_revenue / spend_per_day_unit, 1)

        # 5. Month-by-month cash flow & payback trajectory
        trajectory: List[MonthlyCashFlowPoint] = []
        current_cash = float(working_capital)
        cumulative_profit = 0.0
        min_cash = current_cash
        min_cash_month = 0
        payback_month: Optional[int] = None

        for m in range(1, period_months + 1):
            start_cash = current_cash
            current_cash = round(current_cash + operating_profit, 2)
            cumulative_profit = round(cumulative_profit + operating_profit, 2)

            if current_cash < min_cash:
                min_cash = current_cash
                min_cash_month = m

            if payback_month is None and cumulative_profit >= initial_investment:
                payback_month = m

            trajectory.append(
                MonthlyCashFlowPoint(
                    month=m,
                    starting_cash=start_cash,
                    revenue=monthly_revenue,
                    operating_expenses=total_expenses,
                    operating_profit=operating_profit,
                    ending_cash=current_cash,
                    cumulative_net_profit=cumulative_profit,
                )
            )

        shortfall = min_cash < 0.0
        shortfall_amount = round(abs(min_cash), 2) if shortfall else 0.0

        assumptions = [
            f"Monthly revenue is modeled as: spend (₹{average_customer_spend}) × daily footfall ({expected_customers_per_day}) × {operating_days_per_month} operating days.",
            f"Fixed monthly overhead is ₹{fixed_expenses:,.2f} (rent, salaries, utilities, misc).",
            f"Variable costs (COGS/inventory) are modeled as ₹{variable_expenses:,.2f} per month.",
            f"Initial working capital reserve is ₹{working_capital:,.2f}; initial CapEx is ₹{initial_investment:,.2f}.",
        ]

        limitations = [
            "Projections assume uniform monthly operational performance without seasonal variance or ramp-up phase.",
            "Model does not factor corporate income taxes, goods and services tax (GST), depreciation, or asset amortization.",
            "Debt financing costs, interest expenses, and loan principal repayments are excluded.",
            "Inflationary cost increases and year-over-year revenue escalation are not modeled in this MVP.",
        ]

        return FinancialAnalysisResult(
            currency=currency,
            initial_investment=initial_investment,
            working_capital=working_capital,
            monthly_revenue=monthly_revenue,
            fixed_monthly_expenses=fixed_expenses,
            variable_monthly_expenses=variable_expenses,
            total_monthly_expenses=total_expenses,
            monthly_operating_profit=operating_profit,
            operating_margin_percentage=margin_pct,
            break_even_monthly_revenue=break_even_revenue,
            break_even_daily_customers=break_even_customers,
            is_operationally_profitable=operating_profit > 0,
            payback_period_months=payback_month,
            minimum_cash_balance=min_cash,
            month_of_minimum_cash=min_cash_month,
            cash_shortfall=shortfall,
            shortfall_amount=shortfall_amount,
            cash_flow_trajectory=trajectory,
            assumptions=assumptions,
            limitations=limitations,
        )
