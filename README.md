# Control Room

> Control Room is a tool to set Arnold Settings and Override Settings in an unified UI

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223732642-e7ff20bf-29ac-437e-985a-90c3314047c9.png" width=25%>
  </span>
  <p weight="bold">This tool is closely related to the Render Settings Window</p>
</div>

## How to install

You will need some files that several Illogic tools need. You can get them via this link :
https://github.com/Illogicstudios/common

You must specify the correct path of the installation folder in the ```template_main.py``` file :
```python
if __name__ == '__main__':
    # TODO specify the right path
    install_dir = 'PATH/TO/control_room'
    # [...]
```


---


<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223733969-5268657c-8c93-447c-8129-8b9ea97a7d2a.png" width=80%>
  </span>
  <p weight="bold">Control Room Tool</p>
  <br/>
</div>


## Features


### Feature Overrides

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223731507-1073de6c-101f-4b3b-bde2-b7550f2c0b4b.png" width=80%>
  </span>
  <p weight="bold">Some Arnold settings can be disabled here</p>
  <br/>
</div>


### Depth of Field

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223732923-da35eb45-fba6-468a-87de-c1f306b2b29b.png" width=80%>
  </span>
  <p weight="bold">A camera can be selected here</p>
  <br/>
</div>

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223733272-bcb9e5d8-d683-4220-84ba-58d779a88c26.png" width=80%>
  </span>
  <p weight="bold">Its depth of field can be modified here</p>
  <br/>
</div>


### Motion Blur

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223733528-428c53ac-26bc-4bdf-9a18-20a6923d8789.png" width=80%>
  </span>
  <p weight="bold">Motion Blur settings can be modified here</p>
  <br/>
</div>


### Image Size

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223734288-69291449-76a6-45bd-9fb1-9d4e8aef8dc4.png" width=80%>
  </span>
  <p weight="bold">The image size and aspect ratio can be modified here. It is related to the camera selected earlier</p>
  <br/>
</div>


### Sampling and Adaptive Sampling

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223734610-a1004573-02da-4c90-bdfb-633a718e39ab.png" width=80%>
  </span>
  <p weight="bold">Sampling settings can be modified here</p>
  <br/>
</div>


### Presets

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223735180-a62534ed-6b8e-4b01-bf34-32a5fad7dbf2.png" width=80%>
  </span>
  <p weight="bold">Presets can be created here</p>
  <br/>
</div>

The presets are saved in the scene so they can be retrieved later.

Once a new presets is created, 4 actions are possible : 
- Load and apply this preset
- Rename the preset
- Save the current settings to this preset
- Delete this preset


### Overrides

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/223737349-5bed5525-4a11-4652-996f-ed79b7be3077.png" width=100%>
  </span>
  <p weight="Overrides can be created or removed from the Control Room"></p>
  <br/>
</div>

If a render layer is found in the scene, overrides can be created for some settings. 
To create or remove an override right-click on the field in the UI. If an override exists the fields will be 
displayed in orange