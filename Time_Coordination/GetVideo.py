from Modules import os, t, sht, gp
from Base import mess


class Paths(object):
    def __init__(self):
        self.pathList = ['desktop', 'tempdir', 'videoStorage']
        self.videoinput()

    def create_dir(self, dir: str) -> None:
        """
        dir : Name of the directory to be created

        Creates a directory with the name of the input
        """
        attr = self.__dict__
        if dir in attr:
            p = attr[dir]
        else:
            raise AttributeError
        if not os.path.exists(p):
            os.makedirs(p)
        return None

    def delete_dir(self, dir: str) -> None:
        """
        dir : Name of the directory to be deleted

        Deletes a directory with the name of the input
        """
        attr = self.__dict__
        if dir in attr:
            if os.path.exists(attr[dir]):
                sht.rmtree(attr[dir])
        else:
            raise AttributeError

        return None


class MacosPaths(Paths):
    def __init__(self):
        super().__init__()
        self.desktop = '/Users/'+user+'/Desktop'
        self.tempdir = '/Users/'+user+'/Desktop/tempdir'
        self.videoStorage = '/Users/'+user+'/.##temporary storage##'


class WindowsPaths (Paths):
    def __init__(self):
        super().__init__()
        self.desktop = 'C:Users/' + user + '/Desktop'
        self.tempdir = 'C:/Users/' + user + '/Desktop/tempdir'
        self.videoStorage = 'C:/Users/' + user + '/Desktop/.##temporary storage##'


user = gp.getuser()
if os.name == 'nt':
    paths = WindowsPaths()
elif os.name == 'posix':
    paths = MacosPaths()
else:
    raise Break

def videoinput(self) -> None:
    """
    Récupère la vidéo auprès de l'utilisateur.
    """
    self.paths.create_dir('tempdir')
    acceptedFormats = ['mp4', 'mov', 'MOV', 'avi'] ### CHECK IF AVI IS ACCEPTED BY CV2
    isempty = True
    print(mess.B_vi0, end='')
    while isempty:
        if len(os.listdir(self.paths.tempdir)) != 0:
            isempty = False
        t.sleep(0.5)
    _tempdir = os.listdir(self.paths.tempdir)
    ext = _tempdir[0].split('.')[1]
    if len(_tempdir) == 1 and ext in acceptedFormats:
        video = _tempdir[0]
        self.paths.videoinput = self.paths.tempdir + '/' + video
        self.paths.create_dir('videoStorage')
        sht.copy2(self.paths.videoinput, self.paths.videoStorage)
        self.id = str(video)
        self.paths.delete_dir('tempdir')
        return None
    elif len(_tempdir) == 1 and ext not in acceptedFormats:
        print(mess.P_vi1, end='')
        source = self.paths.tempdir + '/' + _tempdir[0]
        destination = self.paths.desktop + '/' + _tempdir[0]
        sht.copy2(source, destination)
        self.paths.delete_dir('tempdir')
        t.sleep(2)
        self.videoinput()
    elif len(_tempdir) > 1:
        print(mess.P_vi2, end='')
        self.paths.delete_dir('tempdir')
        t.sleep(2)
        self.videoinput()