"""
حاسبات مساندة الذكية
=====================
1. حاسبة تكلفة البناء (BOQ)
2. حاسبة الجدوى الاقتصادية (Feasibility Study)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import math

router = APIRouter()


# ============================================================
# 1. حاسبة تكلفة البناء (BOQ)
# ============================================================
class BOQRequest(BaseModel):
    building_area_sqm: float = Field(..., gt=0, description="مساحة المبنى م²")
    cost_per_sqm: float = Field(..., gt=0, description="تكلفة المتر المربع (درهم)")
    project_type: Literal["residential", "commercial", "industrial", "mixed"] = "commercial"
    construction_type: Literal["concrete", "steel", "hybrid"] = "concrete"


class BOQItem(BaseModel):
    category: str
    item: str
    percentage: float
    amount_aed: float


class BOQResponse(BaseModel):
    total_cost: float
    cost_per_sqm: float
    building_area: float
    items: list[BOQItem]
    breakdown_by_category: dict


# BOQ standard percentages (UAE construction standards)
BOQ_PERCENTAGES = {
    "concrete": {
        "الأعمال الإنشائية": {
            "الحفر والردم": 1.5,
            "الخرسانة المسلحة": 22.0,
            "حديد التسليح": 8.5,
            "القوالب": 4.0,
        },
        "الأعمال المعمارية": {
            "البناء (الطوب)": 6.0,
            "اللياسة والمحارة": 4.5,
            "الأرضيات والبلاط": 7.0,
            "الدهانات": 3.5,
            "الأبواب والشبابيك": 6.0,
            "السقف الكاذب": 2.5,
        },
        "الأعمال الكهربائية": {
            "التمديدات الكهربائية": 5.5,
            "اللوحات والمفاتيح": 2.0,
            "الإنارة": 3.5,
            "أنظمة الاتصالات": 1.5,
        },
        "الأعمال الميكانيكية": {
            "التكييف والتهوية": 7.5,
            "السباكة والصرف": 4.0,
            "مكافحة الحريق": 2.5,
        },
        "الأعمال الخارجية": {
            "أعمال الواجهات": 3.5,
            "أعمال الموقع العام": 2.0,
            "التشطيبات الخارجية": 1.5,
        },
        "إدارة المشروع": {
            "الإشراف والإدارة": 1.0,
        },
    }
}


@router.post("/boq", response_model=BOQResponse)
async def calculate_boq(req: BOQRequest):
    """
    حساب جدول الكميات (BOQ) للمشروع
    """
    total_cost = req.building_area_sqm * req.cost_per_sqm
    percentages = BOQ_PERCENTAGES.get(req.construction_type, BOQ_PERCENTAGES["concrete"])
    
    items = []
    breakdown = {}
    
    for category, sub_items in percentages.items():
        category_total = 0
        for item_name, pct in sub_items.items():
            amount = total_cost * (pct / 100)
            items.append(BOQItem(
                category=category,
                item=item_name,
                percentage=pct,
                amount_aed=round(amount, 2)
            ))
            category_total += amount
        breakdown[category] = round(category_total, 2)
    
    return BOQResponse(
        total_cost=round(total_cost, 2),
        cost_per_sqm=req.cost_per_sqm,
        building_area=req.building_area_sqm,
        items=items,
        breakdown_by_category=breakdown,
    )


# ============================================================
# 2. حاسبة الجدوى الاقتصادية (Feasibility Study)
# ============================================================
class FeasibilityRequest(BaseModel):
    # Basic Info
    building_area_sqm: float = Field(..., gt=0)
    land_area_sqm: float = Field(..., gt=0)
    construction_cost_total: float = Field(..., gt=0, description="تكلفة البناء الكلية")
    project_type: Literal["residential", "commercial", "industrial", "retail", "mixed"] = "commercial"
    
    # Rent
    annual_rent_per_sqm: float = Field(..., gt=0, description="إيجار سنوي للمتر")
    rentable_ratio: float = Field(0.85, ge=0.5, le=1.0, description="النسبة القابلة للإيجار")
    occupancy_rate: float = Field(0.90, ge=0.5, le=1.0, description="نسبة الإشغال")
    annual_rent_increase: float = Field(0.03, ge=0, le=0.10, description="الزيادة السنوية للإيجار")
    
    # Study Parameters
    study_years: int = Field(25, ge=1, le=50)
    grace_period_years: int = Field(2, ge=0, le=10, description="سنوات البناء")
    discount_rate: float = Field(0.08, ge=0.01, le=0.30, description="معدل الخصم")
    vacancy_rate: float = Field(0.05, ge=0, le=0.30, description="نسبة الشواغر")
    
    # OPEX (as % of revenue)
    opex_management: float = Field(0.04, ge=0, le=0.20)
    opex_maintenance: float = Field(0.03, ge=0, le=0.20)
    opex_insurance: float = Field(0.01, ge=0, le=0.10)
    opex_utilities: float = Field(0.02, ge=0, le=0.10)
    
    # Land
    land_type: Literal["owned", "leased", "purchased"] = "leased"
    land_cost: float = Field(0, ge=0, description="تكلفة الأرض إن وجدت")
    
    # Financing (Optional)
    loan_amount: float = Field(0, ge=0)
    loan_interest_rate: float = Field(0.05, ge=0, le=0.20)
    loan_years: int = Field(10, ge=1, le=30)
    
    # Exit Strategy (Optional)
    exit_price: float = Field(0, ge=0)
    exit_year: int = Field(0, ge=0)


class FeasibilityResponse(BaseModel):
    # Headline KPIs
    npv: float
    irr: float
    payback_period_years: float
    cap_rate: float
    coc: float  # Cash on Cash Return
    
    # Totals
    total_investment: float
    total_revenue_lifetime: float
    total_opex_lifetime: float
    total_net_profit: float
    
    # Yearly Cash Flows
    yearly_cash_flows: list[dict]
    
    # Analysis
    verdict: str  # "EXCELLENT", "GOOD", "ACCEPTABLE", "POOR"
    verdict_color: str
    insights: list[str]


def calculate_irr(cash_flows: list[float], guess: float = 0.1) -> float:
    """حساب IRR باستخدام Newton-Raphson"""
    if not cash_flows or all(cf == 0 for cf in cash_flows):
        return 0
    
    rate = guess
    for _ in range(100):
        npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
        d_npv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))
        if abs(d_npv) < 1e-10:
            break
        new_rate = rate - npv / d_npv
        if abs(new_rate - rate) < 1e-7:
            return new_rate
        rate = new_rate
        if rate < -0.99:
            rate = -0.99
    return rate


@router.post("/feasibility", response_model=FeasibilityResponse)
async def calculate_feasibility(req: FeasibilityRequest):
    """
    دراسة جدوى اقتصادية شاملة مع NPV, IRR, Payback, Cap Rate, COC
    """
    # Total Investment
    total_investment = req.construction_cost_total + req.land_cost
    
    # Effective rentable area
    effective_area = req.building_area_sqm * req.rentable_ratio
    
    # Year 1 potential revenue
    year1_potential_revenue = effective_area * req.annual_rent_per_sqm
    
    # Cash Flows
    cash_flows = [-total_investment]  # Year 0: Initial investment
    yearly_data = []
    
    cumulative_cash = -total_investment
    payback_year = None
    
    total_revenue_lifetime = 0
    total_opex_lifetime = 0
    
    # Loan calculations
    annual_loan_payment = 0
    if req.loan_amount > 0:
        r = req.loan_interest_rate
        n = req.loan_years
        annual_loan_payment = req.loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    
    for year in range(1, req.study_years + 1):
        # During grace period: no revenue
        if year <= req.grace_period_years:
            revenue = 0
            opex = 0
            loan_payment = 0
            cf = 0
        else:
            year_in_operation = year - req.grace_period_years
            
            # Revenue (with annual increase)
            current_rent = req.annual_rent_per_sqm * (1 + req.annual_rent_increase) ** (year_in_operation - 1)
            potential_revenue = effective_area * current_rent
            
            # Apply occupancy and vacancy
            actual_revenue = potential_revenue * req.occupancy_rate * (1 - req.vacancy_rate)
            revenue = actual_revenue
            
            # OPEX
            total_opex_pct = req.opex_management + req.opex_maintenance + req.opex_insurance + req.opex_utilities
            opex = revenue * total_opex_pct
            
            # Loan payment
            loan_payment = annual_loan_payment if year_in_operation <= req.loan_years else 0
            
            cf = revenue - opex - loan_payment
        
        total_revenue_lifetime += revenue
        total_opex_lifetime += opex
        cumulative_cash += cf
        
        # Add exit value if applicable
        exit_value = 0
        if req.exit_year > 0 and year == req.exit_year:
            exit_value = req.exit_price
            cf += exit_value
            cumulative_cash += exit_value
        
        # Track payback
        if payback_year is None and cumulative_cash > 0:
            payback_year = year
        
        cash_flows.append(cf)
        yearly_data.append({
            "year": year,
            "revenue": round(revenue, 2),
            "opex": round(opex, 2),
            "loan_payment": round(loan_payment, 2),
            "cash_flow": round(cf, 2),
            "cumulative": round(cumulative_cash, 2),
            "exit_value": round(exit_value, 2) if exit_value else 0,
        })
    
    # NPV
    npv = sum(cf / (1 + req.discount_rate) ** i for i, cf in enumerate(cash_flows))
    
    # IRR
    irr = calculate_irr(cash_flows)
    
    # Payback
    if payback_year is None:
        payback_year = req.study_years + 1  # Never paid back
    
    # Cap Rate (Stabilized Year)
    stabilized_year = req.grace_period_years + 3  # 3 years after construction
    if stabilized_year <= req.study_years:
        stabilized_data = yearly_data[stabilized_year - 1]
        noi = stabilized_data["revenue"] - stabilized_data["opex"]
        cap_rate = (noi / total_investment) * 100 if total_investment > 0 else 0
    else:
        cap_rate = 0
    
    # COC (Cash on Cash)
    equity = total_investment - req.loan_amount
    if equity > 0 and stabilized_year <= req.study_years:
        stabilized_cf = yearly_data[stabilized_year - 1]["cash_flow"]
        coc = (stabilized_cf / equity) * 100
    else:
        coc = 0
    
    # Total Net Profit
    total_net_profit = sum(cf for cf in cash_flows)
    
    # Verdict
    if irr > 0.15 and npv > 0:
        verdict = "EXCELLENT"
        verdict_color = "#16a34a"
    elif irr > 0.10 and npv > 0:
        verdict = "GOOD"
        verdict_color = "#22c55e"
    elif irr > 0.05 and npv > 0:
        verdict = "ACCEPTABLE"
        verdict_color = "#f59e0b"
    else:
        verdict = "POOR"
        verdict_color = "#ef4444"
    
    # Insights
    insights = []
    if irr > req.discount_rate:
        insights.append(f"✅ معدل العائد الداخلي ({irr*100:.1f}%) أعلى من معدل الخصم ({req.discount_rate*100:.0f}%)")
    else:
        insights.append(f"⚠️ معدل العائد الداخلي ({irr*100:.1f}%) أقل من معدل الخصم — إعادة دراسة")
    
    if npv > 0:
        insights.append(f"✅ صافي القيمة الحالية موجب ({npv:,.0f} درهم) — المشروع يضيف قيمة")
    else:
        insights.append(f"❌ صافي القيمة الحالية سالب ({npv:,.0f} درهم)")
    
    if payback_year <= 10:
        insights.append(f"🚀 فترة الاسترداد ممتازة ({payback_year} سنة)")
    elif payback_year <= 15:
        insights.append(f"⏳ فترة الاسترداد مقبولة ({payback_year} سنة)")
    else:
        insights.append(f"⚠️ فترة الاسترداد طويلة ({payback_year} سنة)")
    
    if 6 <= cap_rate <= 9:
        insights.append(f"📊 معدل الرسملة ({cap_rate:.1f}%) ضمن المعدل المقبول لأبوظبي")
    
    return FeasibilityResponse(
        npv=round(npv, 2),
        irr=round(irr * 100, 2),
        payback_period_years=round(payback_year, 1),
        cap_rate=round(cap_rate, 2),
        coc=round(coc, 2),
        total_investment=round(total_investment, 2),
        total_revenue_lifetime=round(total_revenue_lifetime, 2),
        total_opex_lifetime=round(total_opex_lifetime, 2),
        total_net_profit=round(total_net_profit, 2),
        yearly_cash_flows=yearly_data,
        verdict=verdict,
        verdict_color=verdict_color,
        insights=insights,
    )
