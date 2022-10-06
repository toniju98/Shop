import {ethers} from "../js/ethers-5.1.esm.min.js";

const checkoutButton = document.getElementById('checkoutButton')
const price = document.getElementById('price_total')
const form = document.getElementById('formCheck');
const forename = form.elements['forename'];
const name = form.elements['name'];
const email = form.elements['email'];
const shipping_address = form.elements['shipping_address'];
const shipping_zip = form.elements['shipping_zip'];

// A Web3Provider wraps a standard Web3 provider, which is
// what MetaMask injects as window.ethereum into each page
const provider = new ethers.providers.Web3Provider(window.ethereum)
const contract_address = "0xbd00a24Cf61D1e3EBC8cABB1A8393e33E6E56e2C";
const to_address = "0xd46bCBfa79446BB6769feAe3E96E71fB5Aa24b53";

//get json abi
async function fetchTokenAbi() {
    const response = await fetch('../static/abis/TheToken.json');
    const abiToken = await response.json();
    return abiToken;
}

//on click on checkout if fields not empty send tokens
checkoutButton.addEventListener('click', async () => {
    if (name.value != "" && forename.value != "" && shipping_address.value != "" && shipping_zip.value != "" && email.value != "") {

        // MetaMask requires requesting permission to connect users accounts
        const accounts = await provider.send("eth_requestAccounts", []);
        const signer = provider.getSigner()
        const abiToken = await fetchTokenAbi()
        send_token(contract_address, price.textContent, to_address, accounts[0], signer, abiToken.abi)
    }
});

//send token function
function send_token(
    contract_address,
    send_token_amount,
    to_address,
    send_account, signer, send_abi
) {


    provider.getGasPrice().then((currentGasPrice) => {
            let gas_price = ethers.utils.hexlify(parseInt(currentGasPrice))
            console.log(`gas_price: ${gas_price}`)
            // general token send
            let contract = new ethers.Contract(
                contract_address,
                send_abi,
                signer
            )
            console.log(send_token_amount)
            // How many tokens?
            let numberOfTokens = ethers.utils.parseUnits(send_token_amount, 18)
            console.log(`numberOfTokens: ${numberOfTokens}`)
            // Send tokens
            contract.transfer(to_address, numberOfTokens).then((transferResult) => {
                form.submit();
            })
        }
    )
}
