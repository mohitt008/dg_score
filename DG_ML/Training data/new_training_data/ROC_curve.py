import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

def plot_roc(actual,prediction):
	false_positive_rate,true_positive_rate, thresholds= roc_curve(actual,prediction)
	roc_auc=auc(false_positive_rate,true_positive_rate)

	plt.title('Reciever Operating Characteristic')
	plt.plot(false_positive_rate,true_positive_rate,'b',label='AUC = %0.2f'%roc_auc)
	plt.legend(loc='lower right')
	plt.plot([0,1],[0,1],'r--')
	plt.xlim([-0.1,1.2])
	plt.ylim([-0.1,1.2])
	plt.ylabel('True Positive Rate')
	plt.xlabel('False Positive Rate')
	plt.show()