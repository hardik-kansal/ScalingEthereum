// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ModelPerformanceTracker {
    struct ModelVariables1 {
        string epsilon;
        uint num_episodes;
        string gamma;
        string alpha;
        string beta;
        uint fc1_dim;
        uint fc2_dim;
        uint memory_size;
        uint batch_size;
    }

    struct ModelVariables2 {
        uint tau;
        uint update_period;
        uint warmup;
    }

    struct PerformanceData {
        uint[] episode_lengths;
        int[] profit_each_episode;
    }

    mapping(string => ModelVariables1) internal modelInitialVariables1;
    mapping(string => ModelVariables2) internal modelInitialVariables2;
    mapping(string => PerformanceData) internal modelPerformance;

    // Function to store initial variables when a model starts training (Part 1)
    function storeInitialVariablesPart1(
        string memory modelName,
        string memory epsilon,
        uint num_episodes,
        string memory gamma,
        string memory alpha,
        string memory beta,
        uint fc1_dim,
        uint fc2_dim,
        uint memory_size,
        uint batch_size
    ) external {
        ModelVariables1 storage variables = modelInitialVariables1[modelName];
        variables.epsilon = epsilon;
        variables.num_episodes = num_episodes;
        variables.gamma = gamma;
        variables.alpha = alpha;
        variables.beta = beta;
        variables.fc1_dim = fc1_dim;
        variables.fc2_dim = fc2_dim;
        variables.memory_size = memory_size;
        variables.batch_size = batch_size;
    }

    // Function to store initial variables when a model starts training (Part 2)
    function storeInitialVariablesPart2(
        string memory modelName,
        uint tau,
        uint update_period,
        uint warmup
    ) external {
        ModelVariables2 storage variables = modelInitialVariables2[modelName];
        variables.tau=tau;
        variables.update_period=update_period;
        variables.warmup=warmup;

    }

    // Function to store performance data of a model
    function storeModelPerformance(
        string memory modelName,
        uint[] memory episode_lengths,
        int[] memory profit_each_episode
    ) external {
        PerformanceData storage data = modelPerformance[modelName];
        data.episode_lengths = episode_lengths;
        data.profit_each_episode = profit_each_episode;
    }

    // Getter function to retrieve initial variables of a model
    function getModelInitialVariables1(string memory modelName) external view returns (ModelVariables1 memory) {
        return modelInitialVariables1[modelName];
    }

    // Getter function to retrieve performance data of a model
    function getModelInitialVariables2(string memory modelName) external view returns (ModelVariables2 memory) {
        return modelInitialVariables2[modelName];
    }

    // Getter function to retrieve performance data of a model
    function getModelPerformance(string memory modelName) external view returns (PerformanceData memory) {
        return modelPerformance[modelName];
    }
}
