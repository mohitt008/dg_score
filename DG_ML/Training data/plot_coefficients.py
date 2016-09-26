import numpy as np
import matplotlib.pyplot as plt

def plot_coefficients(classifier,feature_names, top_features=20):
	coef= classifier.coef_.ravel()
	t_p_c = np.argsort(coef)[-top_features:]
	t_n_c = np.argsort(coef)[:top_features]
	top_coefs = np.hstack([t_n_c,t_p_c])
	#create plot_coefficients
	plt.figure(figsize=(15,5))
	colors = ['red' if c< 0 else 'blue' for c in coef[top_coefs]]
	plt.bar(np.arange(2*top_features),coef[top_coefs],color= colors)
	feature_names = np.array(feature_names)
	plt.xticks(np.arange(1,1 + 2* top_features),feature_names[top_coefs],rotation = 60,ha='right')
	plt.show()