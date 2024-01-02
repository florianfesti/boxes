Existe-t-il une banque de donnée d'image accessible en api ou en local ?
Comment doit je former l'UI pour blender ?
Tab, clic droit, extension a blendercam ? panneau latéral ?


Les images sont dans  static : samples 

- Faire un essai de definition de propriété dynamique

Une erreur qui se repete : redemarer le serveur blender

Bcp d'incertitudes et d'eventuelles possibilités qui me permets pas davanacer pour la création de groupe de propriétés.
Depuis l'UI ? Depuis une page props ? Doit etre registerée dans la fonction register() ? 

En attendant je repars sur l'affichage des attributs de boxes pour voir la hierarchies de l'affichage.

Je crois que je dois retenir que la création d'une propriété se fait obligatoirement en l'assignant à un type existant.

# Assign a custom property to an existing type.
bpy.types.Material.custom_float = bpy.props.FloatProperty(name="Test Property")

Properties can also be updated through update callbacks, app handlers, getters/setters, manually through through snippet execution, and potentially elsewhere though I can’t recall doing so.
Reliance on operators to update props would make many complex addons impossible.

Le temps de chargement ? 
La description qqpart ?
replace le meme svg
join all parts
generator sans images ?
faire un gros clean 
faire un pull request ? cmt mettre a jour mon script vis avis de festi? Un module qui se télécharge ?