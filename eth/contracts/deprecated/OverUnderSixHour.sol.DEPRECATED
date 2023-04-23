// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract OverUnderSixHour {
    string public constant NAME = "OverUnder6Hour";
    // Duration the event will staty active after BETTING_PERIOD ends
    uint256 private constant EVENT_DURATION = 6 hours;
    // Duration the event will allow betting after contract deployment
    uint256 private constant BETTING_PERIOD = 6 hours;
    // Min bet value
    uint256 public constant MIN_BET_AMOUNT = 0.001 ether;
    // Betting fee currently at 0.001 ether
    uint256 public constant BETTING_FEE = 0.0001 ether;
    // BETTING FEE + MIN_BET_AMOUNT
    uint256 public constant BET_PLUS_FEE = MIN_BET_AMOUNT + BETTING_FEE;

    //new players betting over the _priceMark
    address[] public overBetters;
    mapping(address => uint256) overBets;
    //new players betting under the _priceMark
    address[] public underBetters;
    mapping(address => uint256) underBets;

    //balance of overBetters pool
    uint256 public overBettersBalance = 0 ether;
    //balance of underBetters pool
    uint256 public underBettersBalance = 0 ether;
    // balance of fee pool
    uint256 public feePoolBalance = 0 ether;

    // Modifiers will be based on the betting balances starts as x2
    uint256 public overBettingPayoutModifier = 2;
    uint256 public underBettingPayoutModifier = 2;

    //manager is in charge of the contract (creator)
    address public immutable manager;

    //
    uint256 public immutable priceMark;
    uint256 public immutable bettingClose;
    uint256 public immutable eventClose;

    // ETH, BTC only at the moment
    string public assetSymbol;

    // Price of asset at the end of the event
    uint256 public priceAtClose;

    // Flag that indicates if winners have received their payout
    bool public payoutComplete = false;

    /*
        Input values to the contract
        @param: _priceMark: The price mark that betters will bet above or below
        @param: _assetSymbol: Name of the asset that betters are betting on to be abovce or below _priceMark
    */
    constructor(uint256 _priceMark, string memory _assetSymbol) {
        manager = msg.sender;
        assetSymbol = _assetSymbol;
        priceMark = _priceMark;
        bettingClose = block.timestamp + BETTING_PERIOD;
        eventClose = bettingClose + EVENT_DURATION;
    }

    // Get Contract Name
    function getContractName() public pure returns (string memory) {
        return NAME;
    }

    // Get asset symbol (ETH, BTC)
    function getAssetSymbol() public view returns (string memory) {
        return assetSymbol;
    }

    // Get price mark value
    function getPriceMark() public view returns (uint256) {
        return priceMark;
    }

    // Get betting close time
    function getBettingClose() public view returns (uint256) {
        return bettingClose;
    }

    // Get event close time
    function getEventClose() public view returns (uint256) {
        return eventClose;
    }

    // Get under betting payout modifier value
    function getUnderBettingPayoutModifier() public view returns (uint256) {
        uint256 fullModifier = underBettingPayoutModifier * 10**18;
        return fullModifier;
    }

    // Get over betting payout modifier value
    function getOverBettingPayoutModifier() public view returns (uint256) {
        uint256 fullModifier = overBettingPayoutModifier * 10**18;
        return fullModifier;
    }

    // Get betting fee value
    function getBettingFee() public view returns (uint256) {
        return BETTING_FEE;
    }

    // Get contract balance
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // Get over betters balance
    function getOverBettersBalance() public view returns (uint256) {
        return overBettersBalance;
    }

    // Get under betters balance
    function getUnderBettersBalance() public view returns (uint256) {
        return underBettersBalance;
    }

    // Get over betters addresses
    function getOverBettersAddresses() public view returns (address[] memory) {
        return overBetters;
    }

    // Get under betters addresses
    function getUnderBettersAddresses() public view returns (address[] memory) {
        return underBetters;
    }

    // Check if event is over
    function isEventOver() public view returns (bool) {
        if (block.timestamp > eventClose) {
            return true;
        } else {
            return false;
        }
    }

    /*
        Check if user is in the opposite pool they are trying to bet in. Prevent manipulation
        @param (address): userAddress: msg.sender of either betUnder or betOver functions
        @param (bool): isOverBetter: determines which address array is checked against
        @returns: bool
    */
    function checkUserInOtherPool(address userAddress, bool isOverBetter)
        private
        view
        returns (bool)
    {
        if (isOverBetter) {
            for (uint256 i = 0; i < underBetters.length; i++) {
                if (underBetters[i] == userAddress) {
                    return true;
                }
            }
            return false;
        } else {
            for (uint256 i = 0; i < overBetters.length; i++) {
                if (overBetters[i] == userAddress) {
                    return true;
                }
            }
            return false;
        }
    }

    // Check if user in pool
    function checkUserInPool(address userAddress, bool isOverBetter)
        private
        view
        returns (bool)
    {
        if (isOverBetter) {
            for (uint256 i = 0; i < overBetters.length; i++) {
                if (overBetters[i] == userAddress) {
                    return true;
                }
            }
            return false;
        } else {
            for (uint256 i = 0; i < underBetters.length; i++) {
                if (underBetters[i] == userAddress) {
                    return true;
                }
            }
            return false;
        }
    }

    // Player bets event ends with asset price under the priceMark
    function betUnder() public payable balanceRestriction {
        require(block.timestamp < bettingClose);

        bool userInOtherPool;
        bool userInPool;
        uint256 betValue;
        // players can only join one pool per event (Over or Under)
        userInOtherPool = checkUserInOtherPool(msg.sender, false);
        userInPool = checkUserInPool(msg.sender, false);
        require(userInOtherPool != true, "You have already bet over");
        // players must make a min bet of 0.001 ETH + 0.0001 ETH fee
        require(
            msg.value > BET_PLUS_FEE,
            "Must make a minimum bet of 0.001 ETH + 0.0001 ETH fee"
        );
        // add player to underBetters pool
        if (!userInPool) {
            underBetters.push(msg.sender);
        }

        // Value of bet after fee
        betValue = msg.value - BETTING_FEE;
        // add to underBettersBalance
        underBettersBalance += betValue;
        // map under bet to address
        underBets[msg.sender] += betValue;
        // add fee to fee pool balance
        feePoolBalance += BETTING_FEE;
        // calculate payout modifier for under bet payouts
        underBettingPayoutModifier = (overBettersBalance + underBettersBalance + feePoolBalance) / underBettersBalance;

        if (overBettersBalance > 0) {
            // calculate payout modifier for over bet payouts
            overBettingPayoutModifier = (overBettersBalance + underBettersBalance + feePoolBalance) / overBettersBalance;
        }
    }

    // player bets event ends with asset price over the priceMark
    function betOver() public payable balanceRestriction {
        require(block.timestamp < bettingClose);

        bool userInOtherPool;
        bool userInPool;
        uint256 betValue;
        // players can only join one pool per event (Over or Under)
        userInOtherPool = checkUserInOtherPool(msg.sender, true);
        require(userInOtherPool != true, "You have already bet under");
        // players must make a min bet of 0.001 ETH + 0.0001 ETH fee
        require(
            msg.value > BET_PLUS_FEE,
            "Must make a minimum bet of 0.001 ETH + 0.0001 ETH fee"
        );
        // add player to overBetters pool
        if (!userInPool) {
            overBetters.push(msg.sender);
        }

        // Value of bet after fee
        betValue = msg.value - BETTING_FEE;
        // add to overBettersBalance
        overBettersBalance += betValue;
        // map over bet to address
        overBets[msg.sender] += betValue;
        // add fee to fee pool balance
        feePoolBalance += BETTING_FEE;
        // calculate payout modifier for over bet payouts
        overBettingPayoutModifier = (overBettersBalance + underBettersBalance + feePoolBalance) / overBettersBalance;

        if(underBettersBalance > 0) {
            // calculate payout modifier for under bet payouts
            underBettingPayoutModifier = (overBettersBalance + underBettersBalance + feePoolBalance) / underBettersBalance;
        }

    }

    // Transfer betting fee to custodial wallet
    function sendFee() public restricted {
        payable(manager).transfer(BETTING_FEE);
    }

    // Pay winners of event
    function payWinners() public restricted {
        require(block.timestamp > eventClose);

        if (priceAtClose > priceMark) {
            payOverBetters();
        }
        if (priceAtClose < priceMark) {
            payUnderBetters();
        }
    }

    // Payout over betters
    function payOverBetters() private restricted {
        require(priceAtClose > priceMark);

        address winnerAddress;
        uint256 winnerBetValue;
        uint256 payoutValue;

        for (uint256 i = 0; i < overBetters.length; i++) {
            winnerAddress = overBetters[i];
            winnerBetValue = overBets[winnerAddress];
            payoutValue = winnerBetValue * overBettingPayoutModifier;
            payable(winnerAddress).transfer(payoutValue);
        }
    }

    // Payout to under betters
    function payUnderBetters() private restricted {
        require(priceAtClose < priceMark);

        address winnerAddress;
        uint256 winnerBetValue;
        uint256 payoutValue;

        for (uint256 i = 0; i < underBetters.length; i++) {
            winnerAddress = underBetters[i];
            winnerBetValue = underBets[winnerAddress];
            payoutValue = winnerBetValue * underBettingPayoutModifier;
            payable(winnerAddress).transfer(payoutValue);
        }
    }

    // Destroy contract
    function destroyContract() public restricted {
        require(block.timestamp > eventClose, "Event has not finished");
        require(payoutComplete == true, "Payout has not been made");

        address payable managerAddress = payable(manager);

        // Destroy contract and transfer remaining ETH to manager
        selfdestruct(managerAddress);
    }

    modifier restricted() {
        require(msg.sender == manager);
        _;
    }

    modifier balanceRestriction() {
        require(msg.sender.balance > BET_PLUS_FEE);
        _;
    }
}
