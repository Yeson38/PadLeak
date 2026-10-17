## 热点搭建说明
**热点配置**
 ```cmd
netsh wlan set hostednetwork mode=allow ssid=FreeWiFi key=12345678
```
*   `mode=allow`：允许开启承载网络。
*   `ssid`：设置热点的名称（此处设为 FreeWiFi）。
*   `key`：设置热点密码（必须至少 8 位）。

**热点启动**

```cmd
netsh wlan start hostednetwork
```
*   如果提示“已启动承载网络”，说明热点已成功广播。
*   *排障提示：如果提示“无法启动”，可能是网卡被禁用，需进入设备管理器启用，或者执行 `netsh wlan set hostednetwork mode=disallow` 后重新 `allow` 重置。*

**固定静态 IP** ~~此步骤仅为后续代码写死提供便利（逃~~

进入“网络和共享中心” -> “更改适配器设置” -> 右键虚拟网卡 -> IPv4 属性，手动设置：
*   IP 地址：`192.168.173.1`（后续代码我使用了该ip。其他内网ip只要不冲突均可。尽量选择与现有网络不同网段的ip。）
*   子网掩码：`255.255.255.0`
*   *注意：默认网关和 DNS 均留空，或 DNS 指向该 IP 本身。*
