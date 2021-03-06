import gurobipy as gp

from agregation_functions import weighted_sum, OWA, choquet, capacity


def compute_pmr(P, agregation_function, x, y):
    """
    Compute the Pairwise max regret of x with respect to y given the set of observed preferences P
    """

    dim = len(x)
    model = gp.Model()
    model.setParam('OutputFlag', 0)

        # Variables
        #   All the possible weights of the agregation function
    if agregation_function == OWA or agregation_function == weighted_sum :
        weights = [model.addVar(vtype='C', name='w{}'.format(i)) for i in range(dim)]
    
        # Objective
        #   max f(w, y) - f(w, x)
        f = lambda a: agregation_function(weights, a)
        model.setObjective(f(y) - f(x), gp.GRB.MAXIMIZE)

        # Constraints
        #   All preferences have to be respected
        model.addConstrs(f(a) >= f(b) for a,b in P)
        #   Weights must sum to 1
        model.addConstr(sum(weights) == 1)
        #   Weights between 0 and 1:
    
        if f == weighted_sum:
            for w in weights:
                model.addConstr(w <= 1)
                model.addConstr(w >= 0)
            
        elif f == OWA:
            for i in range(len(weights)-1):
                model.addConstr(weights[i] >= weights[i+1])
                model.addConstr(weights[i] <= 1)
                model.addConstr(weights[i+1] >= 0)
    
    if agregation_function == choquet:
        weights = [model.addVar(vtype='C', name='w{}'.format(i)) for i in range(dim**2)]
        f = lambda a: agregation_function(weights, a)
        model.setObjective(f(y) - f(x), gp.GRB.MAXIMIZE)
        c = capacity(dim).set_label
        model.addConstrs(f(a) >= f(b) for a,b in P)
        # constraints of capacity
        weights[0] = 0
        weights[-1] = 1
        for i in range(dim**2-1):
            for j in range(i+1,dim**2-1):
                s1 , s2 = c[i] & c[j] , c[i] | c[j]
                # constraints of supermodularity capacity
                model.addConstr(weights[i] + weights[j] <= weights[c.index(s1)] + weights[c.index(s2)])
                if (c[i] < c[j]):
                    # constraints of monotonicity of capacity
                    model.addConstr(weights[i] <= weights[j])
                    model.addConstr(weights[i] >= 0)
                    model.addConstr(weights[j] <= 1)
    # Solve the model
    model.optimize()
    return model.objVal

def compute_mr(P, agregation_function, x_set, x, dominated):
    """
    Compute the max regret of x with respect to x_set
    """
    list_pmr = []
    for y in x_set:
        pmr = compute_pmr(P, agregation_function, x, y)
        list_pmr.append(pmr)
        if pmr < 0: # If PMR(x,y;P) is strictly negative, then x is necessarily strictly preferred to y
            dominated.append(y)
    mr = max(list_pmr)

    return [x_set[i] for i in range(len(x_set)) if list_pmr[i] == mr], mr


def compute_mmr(P, agregation_function, x_set, dominated):

    """
    Compute the Min Max Regret of x_set according to preferences P
    """
    list_mr = [compute_mr(P, agregation_function, x_set, x , dominated)[1] for x in x_set]
    mmr = min(list_mr)
    return [x_set[i] for i in range(len(x_set)) if list_mr[i] == mmr], mmr


if __name__ == "__main__":
    X = [(4,8), (6,4), (10,2)]
    P = [((4,8), (6,4)), ((4,8), (10,2)), ((6,4), (10, 2))]
    dominated = []
    print(compute_mmr(P, weighted_sum, X, dominated))
    
