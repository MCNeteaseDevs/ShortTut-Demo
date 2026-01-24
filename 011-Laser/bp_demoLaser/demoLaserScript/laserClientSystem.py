# -*- coding: utf-8 -*-
import math

import mod.client.extraClientApi as clientApi

import demoLaserScript.ui.uiMgr as uiMgr
from mod_log import logger

from demoLaserScript.laserConst import ModName, ServerSystemName

ClientSystem = clientApi.GetClientSystemCls()


def calculate_particle_params(start_pos, end_pos):
    x1, y1, z1 = start_pos
    x2, y2, z2 = end_pos

    delta_x = x2 - x1
    delta_y = y2 - y1
    delta_z = z2 - z1

    distance = math.sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)

    if distance > 0:
        norm_dx = delta_x / distance
        norm_dy = delta_y / distance
        norm_dz = delta_z / distance
    else:
        norm_dx, norm_dy, norm_dz = 0.0, 0.0, 0.0

    return {
        "variable.length": distance * 0.5,
        "variable.dx": norm_dx,
        "variable.dy": norm_dy,
        "variable.dz": norm_dz
    }


class LaserClientSystem(ClientSystem):
    """
    该mod的客户端类
    根据服务端推送下来的数据显示通用显示界面
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.ListenForEvent(ModName, ServerSystemName, "PlayParticleEffectClientEvent", self, self.OnPlayParticleEffect)
        self.particleComp = clientApi.GetEngineCompFactory().CreateParticleSystem(None)

    def OnPlayParticleEffect(self, args):
        fromPos = args["from"]
        toPos = args["to"]
        mid = (fromPos[0] + toPos[0]) / 2.0, (fromPos[1] + toPos[1]) / 2.0, (fromPos[2] + toPos[2]) / 2.0
        params = calculate_particle_params(fromPos, toPos)
        particleId = self.particleComp.Create("demo:laser", mid, (0, 0, 0))
        for varName, varValue in params.items():
            self.particleComp.SetVariable(particleId, varName, varValue)

    def Destroy(self):
        pass
