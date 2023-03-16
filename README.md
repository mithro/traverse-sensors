# Traverse Sensor/Hwmon sensor driver staging

These hwmon drivers are for new devices currently not in the mainline Linux kernel.

These drivers are installed via [dkms](https://github.com/dell/dkms) so you do not need to build a full custom kernel to use them. Eventually these drivers will be submitted for inclusion upstream.

## Microchip EMC230X family fan controllers

**A different EMC230x driver is present in Linux 6.1 and later**

However, this upstream driver (originally written by NVIDIA) does not have device tree support.

The kernel maintainers are unwilling to accept any fan controller drivers with DT bindings
until someone creates a "standard" fan controller DT binding. Which is a good idea, but will take some
work.

Around the same time the upstream driver was accepted, we had just finished
rewriting our emc230x driver with full DT support, allowing individual fans to have
different settings.

You can obtain of our improved/rewritten driver from [this patch series](https://patchwork.kernel.org/project/linux-hwmon/patch/20220914053030.8929-2-matt@traverse.com.au/)

At the moment we continue to ship our "original" emc230x drivers as the Ten64 firmware was
setup for them. We may switch to the new driver in a future firmware release,
regardless of what upstream does.

(Even if ours was submitted before the NVIDIA one, it would have been rejected anyway due to the above DT issue)

## Microchip EMC17XX
* Known issues: Needs attribute rework.

## Microchip PAC1934
* Known issues: Needs attribute rework. A reference IIO driver is available on the Microchip website

## Microchip EMC181X
* Draft version - only tested on EMC1813 so far.
