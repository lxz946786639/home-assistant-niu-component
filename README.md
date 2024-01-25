# Update 

增加了对中国大陆小牛电动的支持；国内坐标偏移的处理；其它优化，不定期更新

Adds support for Chinese Mainland Maverick Electric; Restoration of coordinate migration in Chinese Mainland; Other optimizations, periodic updates.

# Installation

1. 打开HACS极速版，添加自定义仓库"Custom repositories"：https://gitee.com/lxz946786639/home-assistant-niu-component

![01](images/01.png)
![02](images/02.png)

2. 回到列表，搜索“niu”关键字，点击进去下载（因为是基于大佬修改，所以stars少的那个就是）

![03](images/03.png)

3. 下载

![04](images/04.png)

4. “设备与服务”添加集成“Niu Scooters”即可。

5. Enjoy

# FAQ

**Q. 需要在config.xml配置相关信息吗？**  
A. 不需要


<br/>

***

<br/>

# Niu E-scooter Home Assistant integration

This is a custom component for Home Assistant to integrate your Niu Scooter.

Now this integration is _asynchronous_ and it is easy installable via config flow.

## Changes:
* Now it will generate automatically a Niu device so all the sensors and the camera will grouped
![auto device](images/niu_integration_device.png)
* If you select the Last track sensor automatically it will create a camera integration, with the rendered image of your last track.
![last track camera](images/niu_integration_camera.png)

With the thanks to pikka97 !!!

## Setup
1. In Home Assistant's settings under "device and services" click on the "Add integration" button.
2. Search for "Niu Scooters" and click on it.
3. Insert your Niu app companion's credentials and select which sensors do you want.
![config flow](images/config_flow_niu_integration.png)
4. Enjoy your new Niu integration :-)

## Known bugs

some people had problems with this version please take the latest 1.o  versions
See https://github.com/marcelwestrahome/home-assistant-niu-component repository
