#!/usr/bin/python

import os
import bz2
import time
import socket
import shutil
import tarfile
import subprocess
import ConfigParser

date = time.strftime("%Y-%m-%d")
config = ConfigParser.RawConfigParser()
config.read('/etc/backupS3.conf')
dst = config.get('global', 'destiny')
bkp_items = config.items('paths')
hostname = socket.gethostname()
s3_bucket = config.get('s3', 'bucket')

def check_dest(dest):
  if not os.path.exists(dest):
    os.makedirs(dest)

def compress(date, dest, files):
  check_dest(dest)
  if os.path.exists(files):
    if os.path.isfile(files):
      data = open(files, 'r').read()
      compress = bz2.BZ2File('%s-%s.bz2' % (files, date), 'wb')
      compress.write(data)
      compress.close()
      files = compress.name
      shutil.move(files, dest)
      return files
    elif os.path.isdir(files):
      compress = tarfile.open('%s/%s-%s.tar.bz2' % (dest, files, date), 'w:bz2')
      compress.add(files)
      compress.close()
    else:
      print "file does'nt exist"

def send_s3(files, bucket):
  cmd = subprocess.Popen(['/usr/bin/s3cmd', '--recursive', '--reduced-redundancy', 'put', files+'/', bucket+'/'+hostname+'/']).wait()
  for x in os.listdir(files):
    os.remove(files+'/'+x)

def main():
  for items, objects in bkp_items:
    compress(date, dst, objects)
  send_s3(dst, s3_bucket)


if __name__ == '__main__':
  main()

