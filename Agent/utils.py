import matplotlib.pyplot as plt
def plot_learning_curve(episode_lengths,profit_eachEpisode, filename, save_plot=False):
    plt.plot(episode_lengths, label='Episode Lengths', color='blue')
    plt.plot(profit_eachEpisode, label='Profits Each Episode', color='orange')
    plt.xlabel('Episode')
    plt.ylabel('Values')
    plt.title('Episode Lengths and Profit_eachEpsiode')
    plt.legend()
    plt.grid()
    if save_plot:
        plt.savefig(filename + '.png')
    plt.show()
