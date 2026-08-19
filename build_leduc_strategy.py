import pickle
from train_leduc import training

if __name__ == "__main__":
    final_strategy = training(10000)

    with open("leduc_strategy.pkl", "wb") as file:
        pickle.dump(final_strategy, file)