#!/usr/bin/env python3
#
# Author:
#  Tamas Jos (@skelsec)
#
import io
import enum
from minidump.common_structs import * 

# https://msdn.microsoft.com/en-us/library/windows/desktop/ms680510(v=vs.85).aspx
class DumpFlags(enum.Enum):
	MINIDUMP_THREAD_INFO_ERROR_THREAD = 0x00000001 #A placeholder thread due to an error accessing the thread. No thread information exists beyond the thread identifier.
	MINIDUMP_THREAD_INFO_EXITED_THREAD = 0x00000004 #The thread has exited (not running any code) at the time of the dump.
	MINIDUMP_THREAD_INFO_INVALID_CONTEXT = 0x00000010 #Thread context could not be retrieved.
	MINIDUMP_THREAD_INFO_INVALID_INFO = 0x00000008 #Thread information could not be retrieved.
	MINIDUMP_THREAD_INFO_INVALID_TEB = 0x00000020 #TEB information could not be retrieved.
	MINIDUMP_THREAD_INFO_WRITING_THREAD = 0x00000002 #This is the thread that called MiniDumpWriteDump.

# https://msdn.microsoft.com/en-us/library/windows/desktop/ms680506(v=vs.85).aspx
class MINIDUMP_THREAD_INFO_LIST:
	def __init__(self):
		self.SizeOfHeader = None
		self.SizeOfEntry = None
		self.NumberOfEntries = None
	
	def parse(buff):
		mtil = MINIDUMP_THREAD_INFO_LIST()
		mtil.SizeOfHeader = int.from_bytes(buff.read(4), byteorder = 'little', signed = False)
		mtil.SizeOfEntry = int.from_bytes(buff.read(4), byteorder = 'little', signed = False)
		mtil.NumberOfEntries = int.from_bytes(buff.read(4), byteorder = 'little', signed = False)
		
		return mtil
		
	
# https://msdn.microsoft.com/en-us/library/windows/desktop/ms680510(v=vs.85).aspx
class MINIDUMP_THREAD_INFO:
	def __init__(self):
		self.ThreadId = None
		self.DumpFlags = None
		self.DumpError = None
		self.ExitStatus = None
		self.CreateTime = None
		self.ExitTime = None
		self.KernelTime = None
		self.UserTime = None
		self.StartAddress = None
		self.Affinity = None
		
	def parse(buff):
		mti = MINIDUMP_THREAD_INFO()
		mti.ThreadId = int.from_bytes(buff.read(4), byteorder = 'little', signed = False)
		try:
			mti.DumpFlags = DumpFlags(int.from_bytes(buff.read(4), byteorder = 'little', signed = False))
		except:
			pass
		mti.DumpError = int.from_bytes(buff.read(4), byteorder = 'little', signed = False)
		mti.ExitStatus = int.from_bytes(buff.read(4), byteorder = 'little', signed = False)
		mti.CreateTime = int.from_bytes(buff.read(8), byteorder = 'little', signed = False)
		mti.ExitTime = int.from_bytes(buff.read(8), byteorder = 'little', signed = False)
		mti.KernelTime = int.from_bytes(buff.read(8), byteorder = 'little', signed = False)
		mti.UserTime = int.from_bytes(buff.read(8), byteorder = 'little', signed = False)
		mti.StartAddress = int.from_bytes(buff.read(8), byteorder = 'little', signed = False)
		mti.Affinity = int.from_bytes(buff.read(8), byteorder = 'little', signed = False)
		return mti
		
class MinidumpThreadInfo:
	def __init__(self):
		self.ThreadId = None
		self.DumpFlags = None
		self.DumpError = None
		self.ExitStatus = None
		self.CreateTime = None
		self.ExitTime = None
		self.KernelTime = None
		self.UserTime = None
		self.StartAddress = None
		self.Affinity = None
		
	def parse(t, buff):
		mti = MinidumpThreadInfo()
		mti.ThreadId = t.ThreadId
		mti.DumpFlags = t.DumpFlags
		mti.DumpError = t.DumpError
		mti.ExitStatus = t.ExitStatus
		mti.CreateTime = t.CreateTime
		mti.ExitTime = t.ExitTime
		mti.KernelTime = t.KernelTime
		mti.UserTime = t.UserTime
		mti.StartAddress = t.StartAddress
		mti.Affinity = t.Affinity
		return mti
		
	def __str__(self):
		return 'ThreadId: %x DumpFlags: %s DumpError: %s ExitStatus: %x CreateTime: %s ExitTime: %s KernelTime: %s UserTime: %s StartAddress: %x Affinity: %d' % \
			(self.ThreadId, self.DumpFlags, self.DumpError, self.ExitStatus, self.CreateTime, self.ExitTime, self.KernelTime, self.UserTime, self.StartAddress, self.Affinity)
		
class MinidumpThreadInfoList:
	def __init__(self):
		self.header = None
		self.infos = []
		
	def parse(dir, buff):
		t = MinidumpThreadInfoList()
		buff.seek(dir.Location.Rva)
		data = buff.read(dir.Location.DataSize)
		chunk = io.BytesIO(data)
		t.header = MINIDUMP_THREAD_INFO_LIST.parse(chunk)
		for i in range(t.header.NumberOfEntries):
			mi = MINIDUMP_THREAD_INFO.parse(chunk)
			t.infos.append(MinidumpThreadInfo.parse(mi, buff))
		
		return t
	
	def __str__(self):
		t  = '== MinidumpMemoryInfoList ==\n'
		for info in self.infos:
			t+= str(info) + '\n' 
		return t