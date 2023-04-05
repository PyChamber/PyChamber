# Adapted from GLPainterItemExample

import numpy as np
import pyqtgraph as pg
import pyqtgraph.functions as fn
from OpenGL.GL import GL
from pyqtgraph.opengl import GLGraphicsItem
from pyqtgraph.Qt import QtCore, QtGui


class GLSphericalGridItem(GLGraphicsItem.GLGraphicsItem):
    def __init__(
        self,
        radius: float,
        theta_line_color="#60798bff",
        theta_tick_color="#60798bff",
        phi_line_color="#60798bff",
        phi_tick_color="#60798bff",
        yz_rad_color="#60798bff",
        xy_rad_color="#60798bff",
        **kwargs,
    ) -> None:
        super().__init__()
        glopts = kwargs.pop("glOptions", "additive")
        self.setGLOptions(glopts)

        self.text = ""
        self.font = QtGui.QFont("Helvetica", 14)

        self.radius = radius
        self._theta_line_color = fn.mkColor(theta_line_color)
        self._theta_tick_color = fn.mkColor(theta_tick_color)
        self._yz_rad_color = fn.mkColor(yz_rad_color)

        self._phi_line_color = fn.mkColor(phi_line_color)
        self._phi_tick_color = fn.mkColor(phi_tick_color)
        self._xy_rad_color = fn.mkColor(xy_rad_color)

        self._n_sides = 36
        self._text_center = self.radius + (self.radius / 7)
        self.thetas = np.linspace(-np.pi, np.pi, self._n_sides)
        self.line_angles = np.arange(-np.pi, np.pi, np.deg2rad(30))
        self.phi_texts = [f"{round(ang)}" for ang in np.rad2deg(self.line_angles)]
        self.theta_texts = [f"{round(ang)}" for ang in np.rad2deg(self.line_angles)]

    def setColors(
        self,
        theta_line_color=None,
        theta_tick_color=None,
        phi_line_color=None,
        phi_tick_color=None,
        yz_rad_color=None,
        xy_rad_color=None,
    ):
        if theta_line_color is not None:
            self._theta_line_color = fn.mkColor(theta_line_color)
        if theta_tick_color is not None:
            self._theta_tick_color = fn.mkColor(theta_tick_color)
        if phi_line_color is not None:
            self._phi_line_color = fn.mkColor(phi_line_color)
        if phi_tick_color is not None:
            self._phi_tick_color = fn.mkColor(phi_tick_color)
        if yz_rad_color is not None:
            self._yz_rad_color = fn.mkColor(yz_rad_color)
        if xy_rad_color is not None:
            self._xy_rad_color = fn.mkColor(xy_rad_color)

        self.update()

    def paint(self):
        self.setupGLState()

        painter = QtGui.QPainter(self.view())
        self.drawGrid()
        self.drawLabels(painter)
        painter.end()

    def drawLabels(self, painter):
        painter.setPen(pg.mkPen("w"))
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)

        modelview = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
        projection = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
        viewport = [0, 0, self.view().width(), self.view().height()]
        painter.setFont(self.font)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)

        painter.setPen(self._theta_tick_color)
        for angle, label in zip(self.line_angles, self.theta_texts, strict=True):
            y = self._text_center * np.sin(angle)
            z = self._text_center * np.cos(angle)
            pos = np.array([0.0, y, z])
            text_pos = self.__text_project(pos, modelview, projection, viewport)
            text_pos.setY(viewport[3] - text_pos.y())
            painter.drawText(text_pos, label)

        painter.setPen(self._phi_tick_color)
        for angle, label in zip(self.line_angles, self.phi_texts, strict=True):
            x = self._text_center * np.cos(angle)
            y = self._text_center * np.sin(angle)
            pos = np.array([x, y, 0.0])
            text_pos = self.__text_project(pos, modelview, projection, viewport)
            text_pos.setY(viewport[3] - text_pos.y())
            painter.drawText(text_pos, label)

    def drawGrid(self):
        radius = self.radius

        xs = radius * np.cos(self.thetas)
        ys = radius * np.sin(self.thetas)
        zs = radius * np.cos(self.thetas)

        xstarts = radius / 3 * np.cos(self.line_angles)
        ystarts = radius / 3 * np.sin(self.line_angles)
        zstarts = radius / 3 * np.cos(self.line_angles)
        xends = (radius + radius / 10) * np.cos(self.line_angles)
        yends = (radius + radius / 10) * np.sin(self.line_angles)
        zends = (radius + radius / 10) * np.cos(self.line_angles)

        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor4f(*self._xy_rad_color.getRgbF())
        for x, y in zip(xs, ys, strict=True):
            GL.glVertex3f(x, y, 0)
        GL.glEnd()

        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor4f(*self._yz_rad_color.getRgbF())
        for y, z in zip(ys, zs, strict=True):
            GL.glVertex3f(0, y, z)
        GL.glEnd()

        GL.glBegin(GL.GL_LINES)
        GL.glColor4f(*self._phi_line_color.getRgbF())
        for i in range(len(xstarts)):
            GL.glVertex3f(xstarts[i], ystarts[i], 0)
            GL.glVertex3f(xends[i], yends[i], 0)
        GL.glEnd()

        GL.glBegin(GL.GL_LINES)
        GL.glColor4f(*self._theta_line_color.getRgbF())
        for i in range(len(xstarts)):
            GL.glVertex3f(0, ystarts[i], zstarts[i])
            GL.glVertex3f(0, yends[i], zends[i])
        GL.glEnd()

    def __text_project(self, obj_pos, modelview, projection, viewport):
        obj_vec = np.append(np.array(obj_pos), [1.0])

        view_vec = np.matmul(modelview.T, obj_vec)
        proj_vec = np.matmul(projection.T, view_vec)

        if proj_vec[3] == 0.0:
            return QtCore.QPointF(0, 0)

        proj_vec[0:3] /= proj_vec[3]

        return QtCore.QPointF(
            viewport[0] + (1.0 + proj_vec[0]) * viewport[2] / 2, viewport[1] + (1.0 + proj_vec[1]) * viewport[3] / 2
        )
