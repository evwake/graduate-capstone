from matplotlib import pyplot as plt
import json

with open('training_loss.json', 'r') as f:
    training_loss = json.load(f)

with open('training_val_loss.json', 'r') as f:
    training_val_loss = json.load(f)

plt.plot(training_loss, label="Loss")
plt.plot(training_val_loss, label="Validation Loss")
plt.legend()
plt.xlabel("Epoch")
plt.ylabel("Loss Function Value")
plt.show()
