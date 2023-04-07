# Adapted from GLPainterItemExample

import numpy as np
import pyqtgraph as pg
import pyqtgraph.functions as fn
from OpenGL import GL
from pyqtgraph.opengl import GLGraphicsItem
from pyqtgraph.Qt import QtCore, QtGui


class GLSphericalGridItem(GLGraphicsItem.GLGraphicsItem):
    def __init__(
        self,
        radius: float,
        phi_color="#353535FF",
        theta_color="#353535FF",
        **kwargs,
    ) -> None:
        super().__init__()
        glopts = kwargs.pop("glOptions", "additive")
        self.setGLOptions(glopts)

        self.text = ""
        self.font = QtGui.QFont("Helvetica", 14)

        self.radius = radius
        self._phi_color = fn.mkColor(phi_color)
        self._theta_color = fn.mkColor(theta_color)

        self._n_sides = 36
        self._text_center = self.radius + (self.radius / 7)
        self.thetas = np.linspace(-np.pi, np.pi, self._n_sides)
        self.line_angles = np.arange(-np.pi, np.pi, np.deg2rad(30))
        self.phi_texts = [f"{round(ang)}" for ang in np.rad2deg(self.line_angles)]
        self.theta_texts = [f"{round(ang)}" for ang in np.rad2deg(self.line_angles)]

    def setColors(
        self,
        phi_color=(96, 121, 139, 255),
        theta_color=(96, 121, 139, 255),
    ):
        self._phi_color = fn.mkColor(phi_color)
        self._theta_color = fn.mkColor(theta_color)
        self.update()

    def paint(self):
        self.setupGLState()
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

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

        painter.setPen(self._theta_color)
        for angle, label in zip(self.line_angles, self.theta_texts, strict=True):
            y = self._text_center * np.sin(angle)
            z = self._text_center * np.cos(angle)
            pos = np.array([0.0, y, z])
            text_pos = self.__text_project(pos, modelview, projection, viewport)
            text_pos.setY(viewport[3] - text_pos.y())
            painter.drawText(text_pos, label)

        painter.setPen(self._phi_color)
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

        GL.glLineWidth(3)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor4f(*self._phi_color.getRgbF())
        for x, y in zip(xs, ys, strict=True):
            GL.glVertex3f(x, y, 0)
        GL.glEnd()

        GL.glBegin(GL.GL_LINES)
        for i in range(len(xstarts)):
            GL.glVertex3f(xstarts[i], ystarts[i], 0)
            GL.glVertex3f(xends[i], yends[i], 0)
        GL.glEnd()

        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor4f(*self._theta_color.getRgbF())
        for y, z in zip(ys, zs, strict=True):
            GL.glVertex3f(0, y, z)
        GL.glEnd()

        GL.glBegin(GL.GL_LINES)
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
