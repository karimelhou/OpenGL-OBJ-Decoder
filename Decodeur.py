import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Face:
    def __init__(self, vertices):
        self.vertices = vertices  

class Object3D:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.faces = []

def decode_obj_file(filename):
    objects = {}
    global_vertices = []  
    current_object = None

    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('g '):  
                    if current_object:
                        objects[current_object.name] = current_object
                    object_name = line.split()[1].strip()
                    current_object = Object3D(object_name)
                elif line.startswith('v '):  
                    parts = line.split()
                    vertex = Vertex(float(parts[1]), float(parts[2]), float(parts[3]))
                    global_vertices.append(vertex)
                elif line.startswith('f ') and current_object:
                    vertex_indices = [int(part.split('/')[0]) for part in line.split()[1:]]
                    face = Face(vertex_indices)
                    current_object.faces.append(face)
        if current_object:  
            objects[current_object.name] = current_object
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except Exception as e:
        print(f"Error reading file: {e}")

    return objects, global_vertices




def list_objects(objects):
    for name in objects:
        print(f"Object: {name}")


def display_object(obj, global_vertices, display_mode):
    if not glfw.init():
        return

    window = glfw.create_window(640, 640, 'OBJ Viewer', None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(obj, global_vertices, display_mode)  
        glfw.swap_buffers(window)

    glfw.terminate()

def render(obj, global_vertices, display_mode):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

    if display_mode == 'PointCloud':
        render_point_cloud(obj, global_vertices)
    elif display_mode == 'Wireframe':
        render_wireframe(obj, global_vertices)
    elif display_mode == 'Solid':
        render_solid(obj, global_vertices)


def render_point_cloud(obj, global_vertices):
    glPointSize(5)
    glBegin(GL_POINTS)
    for face in obj.faces:
        for idx in face.vertices:
            if 0 <= idx - 1 < len(global_vertices):
                vertex = global_vertices[idx - 1]
                glVertex3f(vertex.x, vertex.y, vertex.z)
    glEnd()


def render_wireframe(obj, global_vertices):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_LINES)
    for face in obj.faces:
        for idx in face.vertices:
            if 0 <= idx - 1 < len(global_vertices):
                vertex = global_vertices[idx - 1]
                glVertex3f(vertex.x, vertex.y, vertex.z)
            else:
                print(f"Skipping invalid vertex index: {idx}")
    glEnd()



def render_solid(obj, global_vertices):
    glBegin(GL_TRIANGLES)
    for face in obj.faces:
        for idx in face.vertices:
            if 0 <= idx - 1 < len(global_vertices):
                vertex = global_vertices[idx - 1]  
                glVertex3f(vertex.x, vertex.y, vertex.z)
            else:
                print(f"Skipping invalid vertex index: {idx}")
    glEnd()


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def save_object_to_file(obj, global_vertices, filename):
    with open(filename, 'w') as file:
        file.write(f'o {obj.name}\n')
        file.write(f'g {obj.name}\n')

        written_vertices = {}
        vertex_index = 1

       
        for face in obj.faces:
            for idx in face.vertices:
                if idx not in written_vertices:
                    vertex = global_vertices[idx - 1]
                    file.write(f'v {vertex.x} {vertex.y} {vertex.z}\n')
                    written_vertices[idx] = vertex_index
                    vertex_index += 1

            face_indices = [written_vertices[idx] for idx in face.vertices]
            file.write('f ' + ' '.join(str(i) for i in face_indices) + '\n')


def main():
    action = input("Choose action - 1 to display an existing object, 2 to open a saved file: ")

    if action == '1':
        obj_filename = '/Users/karim/Documents/MASTER /MASTER M2/ML/Devoir/Objets3D.obj'
        objects, global_vertices = decode_obj_file(obj_filename)
        list_objects(objects)

        object_name = input("Enter the name of the object to display: ")
        if object_name in objects:
            display_mode = input("Enter display mode (1 for PointCloud, 2 for Wireframe, 3 for Solid): ")
            if display_mode == '1':
                display_mode = 'PointCloud'
            elif display_mode == '2':
                display_mode = 'Wireframe'
            elif display_mode == '3':
                display_mode = 'Solid'
            else:
                print("Invalid display mode.")
                return

            display_object(objects[object_name], global_vertices, display_mode)
        else:
            print(f"Object '{object_name}' not found.")

        save_filename = input("Enter filename to save the object (e.g., 'saved_object.obj'): ")
        if save_filename:
            save_object_to_file(objects[object_name], global_vertices, save_filename)
            print(f"Object '{object_name}' saved to {save_filename}")

    elif action == '2':
        saved_filename = input("Enter the filename of the saved object: ")
        try:
            objects, global_vertices = decode_obj_file(saved_filename)
            list_objects(objects)
            object_name = input("Enter the name of the object to display: ")
            if object_name in objects:
                display_mode = input("Enter display mode (1 for PointCloud, 2 for Wireframe, 3 for Solid): ")
                if display_mode == '1':
                    display_mode = 'PointCloud'
                elif display_mode == '2':
                    display_mode = 'Wireframe'
                elif display_mode == '3':
                    display_mode = 'Solid'
                else:
                    print("Invalid display mode.")
                    return

                display_object(objects[object_name], global_vertices, display_mode)
            else:
                print(f"Object '{object_name}' not found.")
        except Exception as e:
            print(f"Error opening file: {e}")

if __name__ == '__main__':
    main()
