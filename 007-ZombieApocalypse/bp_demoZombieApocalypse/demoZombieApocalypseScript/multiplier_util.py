def hp_multiplier(n, alpha_H=0.01, beta_H=1.7):
    return 1 + alpha_H * (n ** beta_H)

def atk_multiplier(n, alpha_A=0.004, beta_A=1.6):
    return 1 + alpha_A * (n ** beta_A)
