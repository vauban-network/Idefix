import coremltools as ct
import tensorflow as tf

# Charger un modèle TensorFlow
model = tf.keras.models.load_model('/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Models/model_general.h5')

# Convertir vers Core ML
coreml_model = ct.convert(model, source="tensorflow")

# Sauvegarder le modèle Core ML
coreml_model.save('/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Models/model_general_metal.mlmodel')
