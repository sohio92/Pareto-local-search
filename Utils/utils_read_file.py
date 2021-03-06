import matplotlib.pyplot as plt


def read_file(filename):
    """
    Returns the instances defined in a .dat file
    """

    with open(filename, 'r') as f:
        content = [[c for c in l.split(' ') if c not in ["\t", "\n"]] for l in f.readlines()]

    weights, values = [], []
    instance = {"n": None, "W": None, "Objects": [weights, values]}
    for ligne in content:
        if ligne[0] == 'i':
            instance["Objects"][0].append(int(ligne[1]))

            if len(instance["Objects"][1]) == 0:
                    instance["Objects"][1] = [[] for _ in range(len(ligne) - 2)]

            for k in range(len(ligne)-2):
                instance["Objects"][1][k].append(int(ligne[k+2]))

        elif ligne[0] == 'n':
            instance["n"] = int(ligne[1])
        elif ligne[0] == 'W':
            instance["W"] = int(ligne[1])

    return instance


def read_exact_file(filename):
    """
    Read the exact non-dominated solutions in .eff file
    """

    with open(filename, 'r') as f:
        content = [tuple(map(int, l.split('\t'))) for l in f.readlines()]

    return content


def plot_solution(x, ax=None, color='blue'):
    """
    Plot a 2 objectives solution
    """

    if ax is None:  fig, ax= plt.subplots()

    ax.scatter(*x, color=color, s=[5])
    return ax


def plot_non_dominated(non_dominated, ax=None, color='red'):
    """
    Plot a 2 objectives exact solution (the sum of the weights is already known)
    """

    if ax is None:
        fig, ax = plt.subplots()

    for _ in non_dominated:
        ax.scatter([i[0] for i in non_dominated], [i[1]
               for i in non_dominated], color=color, s=[2.5] * len(non_dominated))
    return ax


if __name__ == '__main__':
    fig = plot_non_dominated(read_exact_file("Data/100_items/2KP100-TA-0.eff"))
    plt.show()
