import random
from agregation_function import weighted_sum
from utils import get_random_weights, get_score
from utils_elicitation import compute_mmr, compute_mr, compute_pmr



class User:
    """
    Class that allows the user to choose between the best solutions
    """

    def choose(self, elligibles):
        """
        Choose a solution amongst the given array
        """

        print("Which solution do you prefer?")
        
        for i, sol in enumerate(elligibles):
            print("{} - {}".format(i + 1, sol))
        
        user_input = -1
        while user_input <= 0 or user_input > len(elligibles):
            try:
                user_input = int(input())
            except ValueError:
                pass
        
        print()
        return elligibles[user_input-1]


class DecisionMaker(User):
    """
    Decision maker that holds preference and is able to choose its favourite solution from a given array of proposed solutions
    """

    def __init__(self, agregation_function, dim, weights=None):
        self.agregation_function = agregation_function
        self.weights = weights if weights is not None else get_random_weights(dim)
    
    def choose(self, elligibles):
        """
        Choose a solution amongst the given array
        """
        return max(elligibles, key=lambda x: self.agregation_function(self.weights, x))
    
class Elicitor:
    """
    Incremental elicitation procedure to make recommendations to a decision maker
    """

    def __init__(self, pareto_front, decision_maker, regret_threshold=0.1):
        """
        Pareto front is the approximation of the pareto-optimal solutions of a problem
        """

        self.pareto_front = pareto_front

        self.decision_maker = decision_maker
        self.regret_threshold = regret_threshold # Normalized threshold

        self.user_preferences = [] # P
        self.number_of_question = 0
    
    def query_user(self):
        """
        Query the user for its preferred solution amongst a given array
        """        
       # Until we obtain the optimal solution
        while len(self.pareto_front) > 0: 
            print (len(self.pareto_front) )
            dominated = []
          
                # Make the decision maker choose between two alternatives (Current solution strategy)
                #   Update mmr
            list_index_mmr, mmr = compute_mmr(self.user_preferences, self.pareto_front, dominated)
                
            #   Choose xp in argminMR(x, X; P)
            xp = random.choice(list_index_mmr)
            #   Choose yp in argmaxPMR(xp, y; P)
            yp = random.choice(compute_mr(self.user_preferences, self.pareto_front, xp,dominated)[0])
            #   Ask the user
            choice = self.decision_maker.choose((xp, yp))
            if choice == yp: Notchoice = xp 
            else:  Notchoice = yp 
            #   Add the preference to P
            self.user_preferences.append((xp, yp) if choice == xp else (yp, xp))
                
            dominated.append(Notchoice)
            dominated = list(set(dominated))
            for i in dominated: self.pareto_front.remove(i)
                        
            if len(self.pareto_front) == 0:
                self.pareto_front.append(Notchoice)
            
            if len(self.pareto_front) == 1:
                return compute_mmr(self.user_preferences, self.pareto_front,dominated)

            self.number_of_question += 1
                
        return compute_mmr(self.user_preferences, self.pareto_front,dominated)


if __name__ == "__main__":
    import pickle

    with open("Results/Pareto/2KP200-TA-0_obj={}_crit={}.pkl", "rb") as f:
            pareto_front = pickle.load(f)

    #user = User()
    user = DecisionMaker(weighted_sum, len(pareto_front[0]),(0.9,0.1,0.1,0.8,0.1,0.9))
    elicitor = Elicitor(pareto_front, user)
    print(elicitor.query_user())
    
    print(elicitor.number_of_question, elicitor.pareto_front)