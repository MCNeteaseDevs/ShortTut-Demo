# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoCameraScript.cameraConst as cameraConst
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()
CompFactory = clientApi.GetEngineCompFactory()


class CameraClientSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mCameraComp = None
        self.mViewComp = None
        self.ListenForEvent(
            clientApi.GetEngineNamespace(),
            clientApi.GetEngineSystemName(),
            cameraConst.OnKeyPressInGameEvent,
            self,
            self.OnKeyPressInGame
        )

    def Destroy(self):
        self.UnListenForEvent(
            clientApi.GetEngineNamespace(),
            clientApi.GetEngineSystemName(),
            cameraConst.OnKeyPressInGameEvent,
            self,
            self.OnKeyPressInGame
        )

    def OnKeyPressInGame(self, args):
        if str(args.get("isDown")) != "1":
            return
        if args.get("screenName") != cameraConst.HudScreenName:
            return
        key = str(args.get("key"))
        if key == cameraConst.KEY_DEFAULT:
            self.ApplyDefault()
        elif key == cameraConst.KEY_OFFSET:
            self.ApplyOffsetOnly()
        elif key == cameraConst.KEY_SHOULDER:
            self.ApplyShoulder()

    def ApplyDefault(self):
        self._ApplyCamera(cameraConst.OFFSET_DEFAULT, cameraConst.ANCHOR_DEFAULT)

    def ApplyOffsetOnly(self):
        self._ApplyCamera(cameraConst.OFFSET_SHOULDER, cameraConst.ANCHOR_DEFAULT)

    def ApplyShoulder(self):
        self._ApplyCamera(cameraConst.OFFSET_SHOULDER, cameraConst.ANCHOR_SHOULDER)

    def _EnsureComps(self):
        if self.mCameraComp is None:
            self.mCameraComp = CompFactory.CreateCamera(clientApi.GetLevelId())
        if self.mViewComp is None:
            self.mViewComp = CompFactory.CreatePlayerView(clientApi.GetLocalPlayerId())

    def _ApplyCamera(self, offset, anchor):
        self._EnsureComps()
        if self.mViewComp is None or self.mCameraComp is None:
            logger.info("%s camera comps missing", cameraConst.ClientSystemName)
            return
        self.mViewComp.SetPerspective(1)
        self.mCameraComp.SetCameraOffset(offset)
        self.mCameraComp.SetCameraAnchor(anchor)
