from Modules import os, t, sht, gp
from Base import mess

class PathManager:
    def __init__(self, user):
        self.user = user
        self.desktop=self.get_desktop_path()

    def get_desktop_path(self):
        if os.name == 'nt':
            return f'C:/Users/{self.user}/Desktop'
        elif os.name == 'posix':
            return f'/Users/{self.user}/Desktop'
        else:
            raise Exception("Unsupported OS")

    def delete_dir(self, dir_path):
        if os.path.exists(dir_path):
            sht.rmtree(dir_path)

    def get_or_create_dir(self, dir_name):
        dir_path = f"{self.desktop}/{dir_name}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    #def videoinput(self):
        while True:
            if os.listdir(self.tempdir):
                break
            t.sleep(0.5)
        
        files = os.listdir(self.tempdir)
        if len(files) != 1:
            print(mess.P_vi2, end='')
            self.delete_dir(self.tempdir)
            self.get_or_create_dir_dir(self.tempdir)
            return self.videoinput()

        filename = files[0]
        filepath = os.path.join(self.tempdir, filename)
        ext = filename.split('.')[-1].lower()
        accepted_formats = {'mp4', 'mov', 'avi'}

        if ext in accepted_formats:
            video_storage_path = os.path.join(self.videoStorage, filename)
            sht.move(filepath, video_storage_path)
            self.delete_dir(self.tempdir)
            return video_storage_path
        else:
            print(mess.P_vi1, end='')
            destination = os.path.join(self.desktop, filename)
            sht.move(filepath, destination)
            self.delete_dir(self.tempdir)
            return self.videoinput()

#if __name__ == "__main__":
#user = gp.getuser()
#path_manager = PathManager(user)
#video_path = path_manager.videoinput()
#print(f"Video is ready at {video_path}")
