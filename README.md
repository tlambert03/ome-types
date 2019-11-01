# pyOMElite

pyOMElite is a set of python dataclasses implementing a minimal subset of the
OME data model described here:
http://www.openmicroscopy.org/Schemas/OME/2016-06

the general goal is to provide a more pythonic schema for organizing
microscopy datasets, while borrowing from and keeping with the OME model.
Much of the model has been intentionally excluded (for now at least) in
an attempt to make a clean but functional schema.

- attribute names are generally maintained, though CamelCase is replaced
with snake_case

- when optional references to simple objects are specified
(for instance, `Description{0,1}` or `ExperimenterRef{0,1}`), the preference
is to simple make the reference an attribute of the parent.

- when a class has been included, but attributes of that class have been 
excluded, those unused attributes will be commented out at the bottom of
the dataclass.

- when an object has an attribute with an identically-named "units" attribute,
the units are instead added to the metadata dict for the attribute itself


see also: https://github.com/ome/ome-model/blob/master/ome_model/experimental.py