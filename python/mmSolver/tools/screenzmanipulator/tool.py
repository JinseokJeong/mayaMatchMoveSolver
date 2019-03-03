"""
This tool aims the move manipulator tool at the active viewport camera.
After aiming the move tool at the camera, the screen-space Z axis is
highlighted, ready to be middle-click dragged.
"""
import maya.cmds
import mmSolver.logger
from mmSolver.utils.viewport import get_active_model_editor, \
    get_viewport_camera
import mmSolver.tools.screenzmanipulator.constant as const

LOG = mmSolver.logger.get_logger()


def screen_space_z(camera_tfm):
    """
    Modifies moveManipContext to custom and points one of the axis to
    focus camera.

    :param camera_tfm: Camera to point to
    :type camera_tfm: str
    :return: None
    """

    if not camera_tfm:
        LOG.warning('Please select a viewport')
        return
        
    cam_position = maya.cmds.xform(camera_tfm,
                                   worldSpace=True,
                                   query=True,
                                   translation=True)
    maya.cmds.manipMoveContext('Move',
                               edit=True,
                               mode=6,
                               activeHandle=0,
                               orientTowards=cam_position)
    return


def main():
    """
    Main function toggles between screen-space Z and object
    :return: None
    """
    selection = maya.cmds.ls(sl=True)
    if not selection:
        LOG.warning('Please select a object.')
        return

    active_model_editor = get_active_model_editor()
    if not active_model_editor:
        LOG.warning('Please select a viewport.')
        return

    camera_tfm = get_viewport_camera(active_model_editor)[0]

    if not camera_tfm:
        LOG.warning('Please select a viewport.')
        return
    manip_context = const.MANIP_CONTEXT

    move_manip_mode = maya.cmds.manipMoveContext(manip_context,
                                                 query=True,
                                                 mode=True)

    manip_move_super_context = const.MANIP_MOVE_SUPER_CONTEXT
    maya.cmds.setToolTo(manip_move_super_context)

    move_manip_object = const.MOVE_MANIP_MODE_OBJECT
    move_manip_world = const.MOVE_MANIP_MODE_WORLD
    move_manip_custom = const.MOVE_MANIP_MODE_CUSTOM

    if move_manip_mode == move_manip_object or\
            move_manip_mode == move_manip_world:
        maya.cmds.manipMoveContext(manip_context, edit=True,
                                   mode=move_manip_custom)
        screen_space_z(camera_tfm)
        LOG.warning('manipMoveContext to ScreenZ')

    elif move_manip_mode == 6:
        maya.cmds.manipMoveContext(manip_context, edit=True,
                                   mode=move_manip_object)
        LOG.warning('manipMoveContext to Object')
    return
