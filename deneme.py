import subprocess

komut = input("Komutu girin: ")

try:
    subprocess.run(komut, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f'Hata oluştu: {e}')
else:
    print('Komut çaliştirildi.')
