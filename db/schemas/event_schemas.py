from typing import List, Optional
from pydantic import BaseModel, Field


class ContractInfoModel(BaseModel):
    contract_name: Optional[str] = Field(..., description="Name of the contract")
    contract_address: Optional[str] = Field(..., description="Address of the contract")
    contract_abi: Optional[List] = Field(..., description="ABI of the contract")
    price_mark: Optional[float] = Field(..., description="Price mark of the contract")
    asset_symbol: Optional[str] = Field(..., description="Symbol of the asset")
    betting_close: Optional[int] = Field(..., description="Timestamp of the betting close")
    event_close: Optional[int] = Field(..., description="Timestamp of the event close")
    contract_balance: Optional[float] = Field(..., description="Balance of the contract")
    over_betters_balance: Optional[float] = Field(..., description="Balance of the over betters")
    under_betters_balance: Optional[float] = Field(..., description="Balance of the under betters")
    over_betting_payout_modifier: Optional[float] = Field(..., description="Payout modifier for over betters")
    under_betting_payout_modifier: Optional[float] = Field(..., description="Payout modifier for under betters")
    over_betters_addresses: Optional[List] = Field(..., description="List of addresses of over betters")
    under_betters_addresses: Optional[List] = Field(..., description="List of addresses of under betters")
    is_event_over: Optional[bool] = Field(..., description="Is the event over?")

