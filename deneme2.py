import subprocess


komut1 = "roscore"
komut2 = "gazebo"

try:
    subprocess.run(["gnome-terminal", "--", "bash", "-c", komut1])
    subprocess.run(["gnome-terminal", "--", "bash", "-c", komut2])
except Exception as e:
    print(f'Hata oluştu: {e}')
else:
    print('Komut calisti.')
