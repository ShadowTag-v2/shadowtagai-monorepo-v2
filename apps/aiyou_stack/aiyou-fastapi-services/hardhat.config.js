require("@nomicfoundation/hardhat-toolbox");
require("@openzeppelin/hardhat-upgrades");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {},
    // Add other networks here (e.g., polygonMumbai, polygon)
    // polygonMumbai: {
    //   url: process.env.MUMBAI_RPC_URL,
    //   accounts: [process.env.PRIVATE_KEY],
    // },
  },
};
