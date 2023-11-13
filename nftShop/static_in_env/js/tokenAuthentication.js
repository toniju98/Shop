import {ethers} from "../js/ethers-5.1.esm.min.js";

window.userWalletAddress = null
const loginButton = document.getElementById('loginButton')
const provider = new ethers.providers.Web3Provider(window.ethereum)
const nftContractAddress = "0x06c59CCF7B4D0DB3b90fb1b8ac09a697ED8515d3";
const nodeContractAddress = "0x5A3EBd6a60582d9cC85ea09b5BBaeD0322C6fDC5";
let has_nft = false;
let has_node = false;

async function fetchNftAbi() {
    const response = await fetch('../static/abis/CreateNFT.json');
    const abiNft = await response.json();
    return abiNft;
}

async function fetchNodeAbi() {
    const response = await fetch('../static/abis/CreateNFTNode.json');
    const abiNode = await response.json();
    return abiNode;
}


function toggleButton() {
    if (!window.ethereum) {
        loginButton.innerText = 'MetaMask is not installed'
        loginButton.classList.remove('bg-purple-500', 'text-white')
        loginButton.classList.add('bg-gray-500', 'text-gray-100', 'cursor-not-allowed')
        return false
    }

    loginButton.addEventListener('click', loginWithMetaMask)
}

async function isHolder(nftContractAddress, signer, nodeContractAddress, abiNft, abiNode, account) {
    const nftContract = new ethers.Contract(
        nftContractAddress,
        abiNft,
        signer);

    const nodeContract = new ethers.Contract(
        nodeContractAddress,
        abiNode,
        signer);

    const balanceNft = await nftContract.balanceOf(account)
    console.log(balanceNft.toString())
    const balanceNode = await nodeContract.balanceOf(account)
    console.log(balanceNode.toString())

    if (balanceNft.toString() > 0) {
        has_nft = true
    }

    if (balanceNode.toString() > 0) {
        has_node = true
    }

    if (has_nft || has_node) {
        return true;
    }
    return false;
}

async function loginWithMetaMask() {
    const signer = provider.getSigner()
    const accounts = await window.ethereum.request({method: 'eth_requestAccounts'})
        .catch((e) => {
            console.error(e.message)
            return
        })
    if (!accounts) {
        return
    }
    const nftAbi = await fetchNftAbi()
    const nodeAbi = await fetchNodeAbi()
    const holder = await isHolder(nftContractAddress, signer, nodeContractAddress, nftAbi.abi, nodeAbi.abi, accounts[0])
    //if(holder==true) else delete account if existing
    const getNonce = $.ajax({
        type: "POST",
        url: "http://127.0.0.1:8000/get-nonce/",
        data: {
            'csrfmiddlewaretoken': getCookie('csrftoken'),
            "wallet": accounts[0],
            "has_nft": has_nft
        }
    });
    getNonce.done(async function (response) {
        const message = [
            response.nonce
        ].join("\n")
        const signature = await signer.signMessage(message)
        const verifyUser = $.ajax({
            type: "POST",
            url: "http://127.0.0.1:8000/verify-user/",
            data: {
                'csrfmiddlewaretoken': getCookie('csrftoken'),
                "wallet": accounts[0],
                "signature": signature
            }
        });
        verifyUser.done(function (response) {
            console.log(response.verified)
            if (response.verified) {
                window.userWalletAddress = accounts[0]
                loginButton.innerText = 'Sign out of MetaMask' + "(" + accounts[0] + ")"
                $.ajax({
                    type: "POST",
                    url: "http://127.0.0.1:8000/login-user/",
                    data: {
                        'csrfmiddlewaretoken': getCookie('csrftoken'),
                        "wallet": accounts[0],
                    }
                });
                loginButton.removeEventListener('click', loginWithMetaMask)
                setTimeout(() => {
                    loginButton.addEventListener('click', signOutOfMetaMask)
                }, 200)

            } else {
                //TODO: mistake in verification show error

            }
        })
    })
}

async function signOutOfMetaMask() {
    const accounts = await window.ethereum.request({method: 'eth_requestAccounts'})
        .catch((e) => {
            console.error(e.message)
            return
        })

    if (!accounts) {
        return
    }
    window.userWalletAddress = null
    loginButton.innerText = 'Sign in with MetaMask'
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:8000/logout-user/",
        data: {'csrfmiddlewaretoken': getCookie('csrftoken'), "wallet": accounts[0]}
    });

    loginButton.removeEventListener('click', signOutOfMetaMask)
    setTimeout(() => {
        loginButton.addEventListener('click', loginWithMetaMask)
    }, 200)
}

window.addEventListener('DOMContentLoaded', () => {
    toggleButton()
});