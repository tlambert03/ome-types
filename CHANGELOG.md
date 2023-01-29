# Changelog

## [v0.3.3](https://github.com/tlambert03/ome-types/tree/v0.3.3) (2023-01-29)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.3.2...v0.3.3)

**Fixed bugs:**

- fix: prevent unset color from getting output in the XML [\#164](https://github.com/tlambert03/ome-types/pull/164) ([tlambert03](https://github.com/tlambert03))
- fix: use lax validation by default [\#159](https://github.com/tlambert03/ome-types/pull/159) ([tlambert03](https://github.com/tlambert03))

**Tests & CI:**

- style: update pre-commit, use ruff instead of flake8 [\#160](https://github.com/tlambert03/ome-types/pull/160) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- refactor: init\_subclass instead of metaclass [\#165](https://github.com/tlambert03/ome-types/pull/165) ([tlambert03](https://github.com/tlambert03))
- build: Use hatchling for build backend [\#161](https://github.com/tlambert03/ome-types/pull/161) ([tlambert03](https://github.com/tlambert03))

## [v0.3.2](https://github.com/tlambert03/ome-types/tree/v0.3.2) (2022-11-17)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.3.1...v0.3.2)

**Tests & CI:**

- ci: add dependabot [\#149](https://github.com/tlambert03/ome-types/pull/149) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- build: Remove upper version bound of xmlschema dependency [\#156](https://github.com/tlambert03/ome-types/pull/156) ([ap--](https://github.com/ap--))
- ci\(dependabot\): bump actions/cache from 2 to 3 [\#155](https://github.com/tlambert03/ome-types/pull/155) ([dependabot[bot]](https://github.com/apps/dependabot))
- docs:  Fix readthedocs build [\#154](https://github.com/tlambert03/ome-types/pull/154) ([tlambert03](https://github.com/tlambert03))
- ci\(dependabot\): bump actions/checkout from 2 to 3 [\#152](https://github.com/tlambert03/ome-types/pull/152) ([dependabot[bot]](https://github.com/apps/dependabot))
- ci\(dependabot\): bump actions/setup-python from 2 to 4 [\#151](https://github.com/tlambert03/ome-types/pull/151) ([dependabot[bot]](https://github.com/apps/dependabot))
- feat: support python 3.11 [\#150](https://github.com/tlambert03/ome-types/pull/150) ([tlambert03](https://github.com/tlambert03))

## [v0.3.1](https://github.com/tlambert03/ome-types/tree/v0.3.1) (2022-09-16)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.3.0...v0.3.1)

**Fixed bugs:**

- fix: Update Hex40 definition [\#146](https://github.com/tlambert03/ome-types/pull/146) ([joshmoore](https://github.com/joshmoore))

## [v0.3.0](https://github.com/tlambert03/ome-types/tree/v0.3.0) (2022-05-25)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.10...v0.3.0)

**Implemented enhancements:**

- Performance: Lxml parsing [\#127](https://github.com/tlambert03/ome-types/pull/127) ([Nicholas-Schaub](https://github.com/Nicholas-Schaub))

**Tests & CI:**

- update release action [\#140](https://github.com/tlambert03/ome-types/pull/140) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- fix and test check-manifest [\#142](https://github.com/tlambert03/ome-types/pull/142) ([tlambert03](https://github.com/tlambert03))
- add v0.3.0 changelog [\#141](https://github.com/tlambert03/ome-types/pull/141) ([tlambert03](https://github.com/tlambert03))
- Minor documentation updates [\#139](https://github.com/tlambert03/ome-types/pull/139) ([tlambert03](https://github.com/tlambert03))
- Revert default parser, add FutureWarning for v0.4.0 change [\#138](https://github.com/tlambert03/ome-types/pull/138) ([tlambert03](https://github.com/tlambert03))
- Package reorganization [\#131](https://github.com/tlambert03/ome-types/pull/131) ([tlambert03](https://github.com/tlambert03))
- Bump ipython from 7.15.0 to 7.16.3 in /docs [\#123](https://github.com/tlambert03/ome-types/pull/123) ([dependabot[bot]](https://github.com/apps/dependabot))
- Add changelog generator, and minor release stuff [\#121](https://github.com/tlambert03/ome-types/pull/121) ([tlambert03](https://github.com/tlambert03))

## [v0.2.10](https://github.com/tlambert03/ome-types/tree/v0.2.10) (2021-12-29)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.9...v0.2.10)

**Implemented enhancements:**

- support python 3.10 [\#119](https://github.com/tlambert03/ome-types/pull/119) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- fix built branch [\#120](https://github.com/tlambert03/ome-types/pull/120) ([tlambert03](https://github.com/tlambert03))
- Add `kind` to all shapes types [\#117](https://github.com/tlambert03/ome-types/pull/117) ([tlambert03](https://github.com/tlambert03))

**Tests & CI:**

- rename master to main [\#118](https://github.com/tlambert03/ome-types/pull/118) ([tlambert03](https://github.com/tlambert03))

## [v0.2.9](https://github.com/tlambert03/ome-types/tree/v0.2.9) (2021-08-25)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.8...v0.2.9)

**Implemented enhancements:**

- Better abstract "group" types for Instrument and Union [\#103](https://github.com/tlambert03/ome-types/pull/103) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- fix datetime writing [\#106](https://github.com/tlambert03/ome-types/pull/106) ([tlambert03](https://github.com/tlambert03))
- Unpin xmlschema, fix for newer versions [\#105](https://github.com/tlambert03/ome-types/pull/105) ([tlambert03](https://github.com/tlambert03))

## [v0.2.8](https://github.com/tlambert03/ome-types/tree/v0.2.8) (2021-08-10)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.7...v0.2.8)

**Merged pull requests:**

- use pydantic Color type [\#100](https://github.com/tlambert03/ome-types/pull/100) ([tlambert03](https://github.com/tlambert03))

## [v0.2.7](https://github.com/tlambert03/ome-types/tree/v0.2.7) (2021-07-10)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.6...v0.2.7)

**Merged pull requests:**

- look for ome\_types metadata at layer.metadata\['ome\_types'\] [\#97](https://github.com/tlambert03/ome-types/pull/97) ([tlambert03](https://github.com/tlambert03))

## [v0.2.6](https://github.com/tlambert03/ome-types/tree/v0.2.6) (2021-06-26)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.5...v0.2.6)

**Merged pull requests:**

- update OME tree widget [\#95](https://github.com/tlambert03/ome-types/pull/95) ([tlambert03](https://github.com/tlambert03))
- add xml viewer widget napari plugin [\#94](https://github.com/tlambert03/ome-types/pull/94) ([tlambert03](https://github.com/tlambert03))
- Fix retrieval of non 2016 OME schema [\#92](https://github.com/tlambert03/ome-types/pull/92) ([tlambert03](https://github.com/tlambert03))

## [v0.2.5](https://github.com/tlambert03/ome-types/tree/v0.2.5) (2021-06-14)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.4...v0.2.5)

**Merged pull requests:**

- Fix OME model creation with OME namespace prefix [\#91](https://github.com/tlambert03/ome-types/pull/91) ([tlambert03](https://github.com/tlambert03))
- add py.typed for pep 561 compliance [\#83](https://github.com/tlambert03/ome-types/pull/83) ([tlambert03](https://github.com/tlambert03))
- Make ureg public and test all unit enums in simple\_types [\#82](https://github.com/tlambert03/ome-types/pull/82) ([tlambert03](https://github.com/tlambert03))
- Change aicsimageio tests cache key [\#81](https://github.com/tlambert03/ome-types/pull/81) ([tlambert03](https://github.com/tlambert03))
- Fix built branch [\#80](https://github.com/tlambert03/ome-types/pull/80) ([tlambert03](https://github.com/tlambert03))
- Use Pydantic BaseModel instead of dataclass [\#74](https://github.com/tlambert03/ome-types/pull/74) ([tlambert03](https://github.com/tlambert03))

## [v0.2.4](https://github.com/tlambert03/ome-types/tree/v0.2.4) (2021-02-10)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.3...v0.2.4)

**Merged pull requests:**

- admin/update-build-infra [\#79](https://github.com/tlambert03/ome-types/pull/79) ([evamaxfield](https://github.com/evamaxfield))
- Add aicsimageio test [\#77](https://github.com/tlambert03/ome-types/pull/77) ([tlambert03](https://github.com/tlambert03))
- slight fix to built-branch workflow [\#76](https://github.com/tlambert03/ome-types/pull/76) ([tlambert03](https://github.com/tlambert03))
- Add a built branch [\#75](https://github.com/tlambert03/ome-types/pull/75) ([tlambert03](https://github.com/tlambert03))
- pin xmlschema to 1.4.1 [\#73](https://github.com/tlambert03/ome-types/pull/73) ([tlambert03](https://github.com/tlambert03))
- Pull out `_tiff2xml` from `from_tiff` [\#72](https://github.com/tlambert03/ome-types/pull/72) ([tlambert03](https://github.com/tlambert03))
- feature/pass-kwargs-to-xml [\#69](https://github.com/tlambert03/ome-types/pull/69) ([evamaxfield](https://github.com/evamaxfield))
- Add benchmark option to tests [\#63](https://github.com/tlambert03/ome-types/pull/63) ([tlambert03](https://github.com/tlambert03))

## [v0.2.3](https://github.com/tlambert03/ome-types/tree/v0.2.3) (2020-12-24)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.2...v0.2.3)

**Merged pull requests:**

- patch for xmlschema 1.4.0 [\#62](https://github.com/tlambert03/ome-types/pull/62) ([tlambert03](https://github.com/tlambert03))
- Fix serialization/deserialization of weakrefs [\#61](https://github.com/tlambert03/ome-types/pull/61) ([tlambert03](https://github.com/tlambert03))

## [v0.2.2](https://github.com/tlambert03/ome-types/tree/v0.2.2) (2020-12-21)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.1...v0.2.2)

**Merged pull requests:**

- Add windows and mac tests on CI, add py3.9 [\#59](https://github.com/tlambert03/ome-types/pull/59) ([tlambert03](https://github.com/tlambert03))
- catch long string path exists fail [\#58](https://github.com/tlambert03/ome-types/pull/58) ([tlambert03](https://github.com/tlambert03))

## [v0.2.1](https://github.com/tlambert03/ome-types/tree/v0.2.1) (2020-12-09)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.2.0...v0.2.1)

**Merged pull requests:**

- fix etree parse on literal string [\#56](https://github.com/tlambert03/ome-types/pull/56) ([tlambert03](https://github.com/tlambert03))
- add from\_tiff test [\#55](https://github.com/tlambert03/ome-types/pull/55) ([tlambert03](https://github.com/tlambert03))
- update readme [\#54](https://github.com/tlambert03/ome-types/pull/54) ([tlambert03](https://github.com/tlambert03))

## [v0.2.0](https://github.com/tlambert03/ome-types/tree/v0.2.0) (2020-09-15)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.1.0...v0.2.0)

**Merged pull requests:**

- from\_tiff convenience function [\#51](https://github.com/tlambert03/ome-types/pull/51) ([tlambert03](https://github.com/tlambert03))
- fix xsd:list code gen [\#48](https://github.com/tlambert03/ome-types/pull/48) ([tlambert03](https://github.com/tlambert03))
- add & skip failing test [\#46](https://github.com/tlambert03/ome-types/pull/46) ([tlambert03](https://github.com/tlambert03))
- Add to\_xml for serializing a model to XML [\#44](https://github.com/tlambert03/ome-types/pull/44) ([jmuhlich](https://github.com/jmuhlich))
- update isort [\#42](https://github.com/tlambert03/ome-types/pull/42) ([tlambert03](https://github.com/tlambert03))
- basic api docs [\#41](https://github.com/tlambert03/ome-types/pull/41) ([tlambert03](https://github.com/tlambert03))
- Add docstrings [\#40](https://github.com/tlambert03/ome-types/pull/40) ([tlambert03](https://github.com/tlambert03))
- Add \_quantity property for values with units [\#38](https://github.com/tlambert03/ome-types/pull/38) ([jmuhlich](https://github.com/jmuhlich))
- Fix type for id field of Settings subclasses [\#37](https://github.com/tlambert03/ome-types/pull/37) ([jmuhlich](https://github.com/jmuhlich))
- Update References with pointer to target object [\#34](https://github.com/tlambert03/ome-types/pull/34) ([jmuhlich](https://github.com/jmuhlich))
- Give sentinel objects a distinctive repr [\#32](https://github.com/tlambert03/ome-types/pull/32) ([jmuhlich](https://github.com/jmuhlich))
- Make id fields non-optional but retain auto-numbering [\#31](https://github.com/tlambert03/ome-types/pull/31) ([jmuhlich](https://github.com/jmuhlich))
- Improve sorting of generated code for consistency [\#29](https://github.com/tlambert03/ome-types/pull/29) ([jmuhlich](https://github.com/jmuhlich))
- Use local copy of schema for autogen [\#28](https://github.com/tlambert03/ome-types/pull/28) ([jmuhlich](https://github.com/jmuhlich))

## [v0.1.0](https://github.com/tlambert03/ome-types/tree/v0.1.0) (2020-08-06)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.0.1...v0.1.0)

**Merged pull requests:**

- improved repr [\#26](https://github.com/tlambert03/ome-types/pull/26) ([tlambert03](https://github.com/tlambert03))
- better non-default in subclass solution [\#25](https://github.com/tlambert03/ome-types/pull/25) ([tlambert03](https://github.com/tlambert03))
- make IDs optional, add ome\_dataclass decorator [\#23](https://github.com/tlambert03/ome-types/pull/23) ([tlambert03](https://github.com/tlambert03))
- Rename container fields to plural form [\#22](https://github.com/tlambert03/ome-types/pull/22) ([jmuhlich](https://github.com/jmuhlich))
- Make annotations work [\#21](https://github.com/tlambert03/ome-types/pull/21) ([jmuhlich](https://github.com/jmuhlich))
- no disk caching [\#20](https://github.com/tlambert03/ome-types/pull/20) ([tlambert03](https://github.com/tlambert03))
- Make light sources and shapes work [\#17](https://github.com/tlambert03/ome-types/pull/17) ([jmuhlich](https://github.com/jmuhlich))
- add --nogen option to run tests on pregenerated code [\#14](https://github.com/tlambert03/ome-types/pull/14) ([tlambert03](https://github.com/tlambert03))
- add mypy check on generated code [\#12](https://github.com/tlambert03/ome-types/pull/12) ([tlambert03](https://github.com/tlambert03))
- Improve model for BinData [\#11](https://github.com/tlambert03/ome-types/pull/11) ([jmuhlich](https://github.com/jmuhlich))
- Add OME sample data to tests, and mark with xfail for now [\#10](https://github.com/tlambert03/ome-types/pull/10) ([tlambert03](https://github.com/tlambert03))
- Improve typing hints in generated code [\#7](https://github.com/tlambert03/ome-types/pull/7) ([jmuhlich](https://github.com/jmuhlich))
- Pin isort version to 4.x due to big changes in 5.x [\#6](https://github.com/tlambert03/ome-types/pull/6) ([jmuhlich](https://github.com/jmuhlich))

## [v0.0.1](https://github.com/tlambert03/ome-types/tree/v0.0.1) (2020-05-30)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.0.1rc5...v0.0.1)

## [v0.0.1rc5](https://github.com/tlambert03/ome-types/tree/v0.0.1rc5) (2020-05-30)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.0.1rc4...v0.0.1rc5)

## [v0.0.1rc4](https://github.com/tlambert03/ome-types/tree/v0.0.1rc4) (2020-05-30)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.0.1rc3...v0.0.1rc4)

## [v0.0.1rc3](https://github.com/tlambert03/ome-types/tree/v0.0.1rc3) (2020-05-30)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.0.1rc2...v0.0.1rc3)

## [v0.0.1rc2](https://github.com/tlambert03/ome-types/tree/v0.0.1rc2) (2020-05-30)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/v0.0.1rc1...v0.0.1rc2)

## [v0.0.1rc1](https://github.com/tlambert03/ome-types/tree/v0.0.1rc1) (2020-05-30)

[Full Changelog](https://github.com/tlambert03/ome-types/compare/caec21aaf4de6278b9511b77297e24bc4d7369f7...v0.0.1rc1)

**Merged pull requests:**

- intial setup config [\#1](https://github.com/tlambert03/ome-types/pull/1) ([tlambert03](https://github.com/tlambert03))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
