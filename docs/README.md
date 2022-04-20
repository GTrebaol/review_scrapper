# Mobile-indus

- [Workflow](#workflow)
- [Versioning](#versioning)

## Workflow

- Branch created from develop/release
  - if opened MR : build/quality
  - if not opened MR : all publish in manual
  - if develop : publish rec auto, other in manual
  - if release : publish nrg/hml internal in auto, other in manual

## Versioning

The versionning used by the application is quite different depending on whether it is a fedes or B2B but work on a common core.

### REC

This is the semantic versioning of an application that will be published in the _REC_ environment.

```
X.Y.Z-devN
```

Any version of an application that will be publish in _REC_ will have this semantic versioning. The digits X.Y.Z will be configured by developers in the project and the N digit will be be set up automatically by the CI.

### NRG/HML

Any version of an application that will be publish in _NRG_ will have this semantic versioning. The digits X.Y.Z will be configured by developers in the project and the N digit will be be set up automatically by the CI.

```
X.Y.Z-rcN
```

### PROD

Any version of an application that will be publish in _PROD_ will have this semantic versioning. The digits X.Y.Z will be configured by developers in the project and the N digit will be be set up automatically by the CI.

```
X.Y.Z
```
