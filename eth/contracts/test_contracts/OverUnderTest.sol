// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract OverUnderTest {
    string public constant NAME = "OverUnderTest";
    // Duration the event will staty active after BETTING_PERIOD ends
    uint256 private constant EVENT_DURATION = 20 minutes;
    // Duration the event will allow betting after contract deployment
    uint256 private constant BETTING_PERIOD = 20 minutes;
    // Duration before payouts are automatically sent to winners
    uint256 private constant PAYOUT_PERIOD = 0 hours;
    // Min bet value
    uint256 public constant MIN_BET_AMOUNT = 0.001 ether;
    // Betting fee currently at 0.001 ether
    uint256 public constant BETTING_FEE = 0.0001 ether;
    // BETTING FEE + MIN_BET_AMOUNT
    uint256 public constant BET_PLUS_FEE = MIN_BET_AMOUNT + BETTING_FEE;

    struct Bet {
        uint256 betBalance; // initialize to 0
        uint256 withdrawBalance; // initialize to 0
        bool payoutComplete; // initialize to false
    }
    mapping(address => Bet) underBets;
    mapping(address => Bet) overBets;

    //new players betting over the _priceMark
    address[] public overBetters;
    //new players betting under the _priceMark
    address[] public underBetters;
    // addresses of winners
    address[] public winningBetters;

    //balance of overBetters pool
    uint256 public overBettersBalance = 0 ether;
    //balance of underBetters pool
    uint256 public underBettersBalance = 0 ether;
    // balance of fee pool
    uint256 public feePoolBalance = 0 ether;

    // Modifiers will be based on the betting balances starts as x2
    uint256 public overBettingPayoutModifier = 2000000000000000000;
    uint256 public underBettingPayoutModifier = 2000000000000000000;

    // manager is in charge of the contract (creator)
    address public immutable manager;

    //
    uint256 public immutable priceMark;
    uint256 public immutable bettingClose;
    uint256 public immutable eventClose;
    uint256 public immutable payoutClose;

    // ETH, BTC only at the moment
    string public assetSymbol;

    // Price of asset at the end of the event
    uint256 public priceAtClose;


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
        payoutClose = eventClose + PAYOUT_PERIOD;
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
        return underBettingPayoutModifier;
    }

    // Get over betting payout modifier value
    function getOverBettingPayoutModifier() public view returns (uint256) {
        return overBettingPayoutModifier;
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

    // Get winning betters addresses
    function getWinningBettersAddresses() public view returns (address[] memory) {
        return winningBetters;
    }

    // Check if event is over
    function isEventOver() public view returns (bool) {
        if (block.timestamp > eventClose) {
            return true;
        } else {
            return false;
        }
    }

    function setPriceAtClose(uint256 _price) public restricted {
        require(block.timestamp > eventClose);
        priceAtClose = _price;
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

        uint256 betValue;
        bool userInPool;

        // players must make a min bet of 0.001 ETH + 0.0001 ETH fee
        require(
            msg.value > BET_PLUS_FEE,
            "Must make a minimum bet of 0.001 ETH + 0.0001 ETH fee"
        );

        userInPool = checkUserInPool(msg.sender, false);
        if (!userInPool) {
            // add player to underBetters pool
            underBetters.push(msg.sender);
            underBets[msg.sender] = Bet(0, 0, false); // Initialize new Bet
        }

        // Value of bet after fee
        betValue = msg.value - BETTING_FEE;
        // add to underBettersBalance
        underBettersBalance += betValue * 1 ether;
        // map under bet to address
        underBets[msg.sender].betBalance += betValue * 1 ether;
        // the value of the bet is multiplied by the value of the payout modifier at the time of bet
        underBets[msg.sender].withdrawBalance += (betValue * underBettingPayoutModifier) * 1 ether;
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

        uint256 betValue;
        bool userInPool;

        // players must make a min bet of 0.001 ETH + 0.0001 ETH fee
        require(
            msg.value > BET_PLUS_FEE,
            "Must make a minimum bet of 0.001 ETH + 0.0001 ETH fee"
        );

        userInPool = checkUserInPool(msg.sender, true);
        if (!userInPool) {
            overBetters.push(msg.sender);
            overBets[msg.sender] = Bet(0, 0, false); // Initialize new Bet
        }

        // Value of bet after fee
        betValue = msg.value - BETTING_FEE;
        // add to overBettersBalance
        overBettersBalance += betValue * 1 ether;
        // map over bet to address
        overBets[msg.sender].betBalance += betValue * 1 ether;
        // the value of the bet is multiplied by the value of the payout modifier at the time of bet
        overBets[msg.sender].withdrawBalance += (betValue * overBettingPayoutModifier) * 1 ether;
        // add fee to fee pool balance
        feePoolBalance += BETTING_FEE;
        // calculate payout modifier for over bet payouts
        overBettingPayoutModifier = (overBettersBalance + underBettersBalance + feePoolBalance) / overBettersBalance;

        if(underBettersBalance > 0) {
            // calculate payout modifier for under bet payouts
            underBettingPayoutModifier = (overBettersBalance + underBettersBalance + feePoolBalance) / underBettersBalance;
        }

    }

    function populateWinners(address[] memory winningAdresses) private {
        for (uint256 i = 0; i < winningAdresses.length; i++) {
            winningBetters.push(winningAdresses[i]);
        }
    }

    // Function to be called via python process
    function setWinners() public restricted {
        require(block.timestamp > eventClose);
        if (priceAtClose > priceMark) {
            populateWinners(overBetters);
        }
        if (priceAtClose < priceMark) {
            populateWinners(underBetters);
        }
    }

    // Function to be called by winning betters.
    // Will block any betters that are not in winningBetters array
    function winnerWithdrawFunds() public withdrawRestriction(winningBetters) {

        if (priceAtClose > priceMark) {
            require(overBets[msg.sender].payoutComplete == false);
            payable(msg.sender).transfer(overBets[msg.sender].withdrawBalance);
            overBets[msg.sender].payoutComplete = true;
        }
        if (priceAtClose < priceMark) {
            require(underBets[msg.sender].payoutComplete == false);
            payable(msg.sender).transfer(underBets[msg.sender].withdrawBalance);
            underBets[msg.sender].payoutComplete = true;
        }
    }

    // Destroy contract
    function destroyContract() public restricted {
        require(block.timestamp > payoutClose, "Event has not finished");

        address payable managerAddress = payable(manager);

        // Destroy contract and transfer winnings to remaining betters that have not withdrawn
        // TODO: Apply penalty to betters that have not withdrawn
        for(uint256 i = 0; i < winningBetters.length; i++) {
            if (priceAtClose > priceMark) {
                if (overBets[winningBetters[i]].payoutComplete == false) {
                    payable(winningBetters[i]).transfer(overBets[winningBetters[i]].withdrawBalance);
                }
            }
            if (priceAtClose < priceMark) {
                if (underBets[winningBetters[i]].payoutComplete == false) {
                    payable(winningBetters[i]).transfer(underBets[winningBetters[i]].withdrawBalance);
                }
            }
        }

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

    modifier withdrawRestriction(address[] memory allowedAddresses) {
        bool allowed = false;
        for (uint256 i = 0; i < allowedAddresses.length; i++) {
            if (allowedAddresses[i] == msg.sender) {
                allowed = true;
                break;
            }
        }
        require(allowed, "Access denied");
        _;
    }

}
