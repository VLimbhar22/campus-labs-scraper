import pickle

progress_variables = {'campus': 0, 'organization': 0}
with open('input/progress.pkl', 'wb') as f:
    pickle.dump(progress_variables, f)
