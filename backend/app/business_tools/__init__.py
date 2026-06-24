from app.business_tools.crm.hubspot import (
    HubSpotCustomerHistoryTool,
    HubSpotCustomerValueTool,
    HubSpotLookupCustomerTool,
    HubSpotOpportunitiesTool,
)
from app.business_tools.erp.odoo import (
    CheckBudgetsTool,
    CreatePurchaseOrderTool,
    CreateRfqTool,
    GetReorderThresholdsTool,
    ValidateApprovalsTool,
)
from app.business_tools.logistics.dhl_gig import (
    CheckShippingRoutesTool,
    EstimateShippingCostTool,
    TrackShipmentTool,
    ValidateDeliveryFeasibilityTool,
)
from app.business_tools.payments.paystack import (
    AssessCreditRiskTool,
    CheckTransactionHistoryTool,
    RecommendPaymentTermsTool,
    VerifyPaymentTool,
)
from app.business_tools.registry import ToolRegistry
from app.business_tools.simulated.inventory import CheckAvailabilityTool, GetProductSpecsTool
from app.business_tools.simulated.onboarding import CheckCreditTool, CheckKycTool, VerifyDocumentsTool
from app.business_tools.simulated.policies import CheckPolicyTool, GetAllPoliciesTool
from app.business_tools.simulated.pricing import CalculatePriceTool, GetExchangeRateTool
from app.business_tools.simulated.suppliers import FindSuppliersTool, GetSupplierTool

tool_registry = ToolRegistry()

for tool in [
    CalculatePriceTool(),
    GetExchangeRateTool(),
    CheckAvailabilityTool(),
    GetProductSpecsTool(),
    FindSuppliersTool(),
    GetSupplierTool(),
    CheckPolicyTool(),
    GetAllPoliciesTool(),
    CheckKycTool(),
    CheckCreditTool(),
    VerifyDocumentsTool(),
    HubSpotLookupCustomerTool(),
    HubSpotCustomerHistoryTool(),
    HubSpotOpportunitiesTool(),
    HubSpotCustomerValueTool(),
    CreateRfqTool(),
    CreatePurchaseOrderTool(),
    CheckBudgetsTool(),
    ValidateApprovalsTool(),
    GetReorderThresholdsTool(),
    VerifyPaymentTool(),
    CheckTransactionHistoryTool(),
    AssessCreditRiskTool(),
    RecommendPaymentTermsTool(),
    EstimateShippingCostTool(),
    ValidateDeliveryFeasibilityTool(),
    CheckShippingRoutesTool(),
    TrackShipmentTool(),
]:
    tool_registry.register(tool)
