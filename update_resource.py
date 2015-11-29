#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#created by zhuhui

import os
import sys

#注意点
#1. 仅仅适用于cocos2d-js
#2. 该文件默认放在工程的根目录
#3. 如果工程目录结构发生更改，要根据实际修改 #环境配置#

#包含功能
#1. 更新resource.js文件，资源无需手动管理，只要管理号res目录下的文件夹即可
#2. 代码行数统计 - 可统计src目录下的js文件和Classes文件夹内的.h .cpp文件

################ 环境配置 ##################

#项目根路径
project_root = os.path.dirname(__file__)

#res路径
res_root = os.path.join(project_root, "res")

#resource.js 路径
resource_js_path = os.path.join(project_root, "src/resource.js")

#src路径
src_root = os.path.join(project_root, "src")

#runtime-src路径
runtimesrc_root = os.path.join(project_root, "frameworks/runtime-src")

#Classes路径
classes_root = os.path.join(runtimesrc_root, "Classes")

################ 环境配置 end ################

######################## resource.js 生成规则 ##########################
#遍历res_root目录，如果文件后缀名在以下列表中，就添加到resource.js中，应根据实际自由设置
res_extension_list = [".png", ".jpg", ".plist", ".wav", ".mp3"];

#遍历res_root中的子目录列表，非递归!! 仅对一级目录有效,如想只遍历res/ui/numbers是不行的
res_dirs = ["ui", "sounds"]

#某些文件名相同，但扩展名不同，这样会产生冲突，遇到这种情况，需要修改此列表, 如abc.plist -> res.abc_plist
res_special = {".plist":"_plist"}; 
###################### resource.js 生成规则 end ########################


############### 代码统计规则 #####################

#不参与统计的js文件
iginore_js_file = ["app.js", "resource.js"]

#统计c++文件的扩展名
cpp_extension_list =  [".h", ".cpp", ".c", ".cpp", ".cc"]
#忽略的文件
iginore_cpp_file = ["sqlite3.c", "sqlite3.h"]
############ 代码统计规则 end ####################


######################################    以下内容不用管了    ######################################


resource_js_template = """
var res = {
	{{resources}}
};
g_resources = [];
for (var i in res) {
    g_resources.push(res[i]);
}
"""

def search_res():
	"""
	:return: [ ("res/xxx/xxx.xxx", "xxx", ".xxx"), ... ]
	"""
	resList = []
	print "--------"+res_root
	for parent, dirnames, filenames in os.walk(res_root):
		for filename in filenames:
			absFileName = os.path.join(parent, filename)
			filename = os.path.relpath(absFileName, res_root)
			if filename.find("/") == -1:
				continue
			reldirname = filename[:filename.find("/")]
			relfilename = filename[filename.rfind("/")+1:]
			extensionname = relfilename[relfilename.find("."):]
			if (reldirname in res_dirs) and (extensionname in res_extension_list):
				resList.append((os.path.relpath(absFileName, project_root),relfilename[:relfilename.find(".")], extensionname))
	return resList

def update_resource_js(filename, resList):
	"""
	write the resource.js to the resource_js_path
	:return: None
	"""
	count = {}
	ls = []
	keyNameList = []
	for fullname, name, extensionname in resList:
		keyName = name
		if extensionname in res_special.keys():
			keyName = name + res_special[extensionname]
		if extensionname in res_extension_list:
			if extensionname in count:
				count[extensionname] += 1
			else:
				count[extensionname] = 1
		if keyName in keyNameList:
			print "warning: 存在冲突的文件: %s 请修改 res_special 列表" % fullname
			continue
		else:
			keyNameList.append(keyName)
			ls.append('%s : "%s"' % (keyName, fullname))
	content = ",".join(ls)

	print "\n-- 资源统计 --"
	print count


	try:
		f = open(filename, "w+")
		fileContent = resource_js_template.replace("{{resources}}", content)
		f.write(fileContent)
		f.close()
		print "写入 %s 成功" % filename
	except:
		print "写入 %s 失败!!!!" % filename


def statistics_js_line(jsdirname):
	"""
	:param jsdirname: js代码存放目录
	:return: [ (filename, lineCount), ... ]
	"""
	ls = []
	for p,d,n in os.walk(jsdirname):
		for fileName in n:
			fullFile = os.path.join(p, fileName)
			if fileName.endswith(".js") and not fileName in iginore_js_file:
				str = None
				try:
					f = open(fullFile)
					str = f.read()
					f.close()
				except:
					print "打开 %s 失败" % fullFile
					continue
				ls.append(( os.path.relpath(fullFile, src_root), len(str.split("\n"))))
	return ls

def statistics_cpp_line(cppdirname):
	ls = []
	for p,d,n in os.walk(cppdirname):
		for fileName in n:
			fullFile = os.path.join(p, fileName)
			extensionname = fileName[fileName.find("."):]
			if extensionname in cpp_extension_list and not fileName in iginore_cpp_file:
				str = None
				try:
					f = open(fullFile)
					str = f.read()
					f.close()
				except:
					print "打开 %s 失败" % fullFile
					continue
				ls.append((os.path.relpath(fullFile, src_root), len(str.split("\n"))))
	return ls


if __name__ == '__main__':    
	resList = search_res()
	update_resource_js(resource_js_path, resList)

	jsCountLine = 0
	js_srclist = statistics_js_line(src_root)
	for filename, lineCount in js_srclist:
		#print "%s - %d" % (filename, lineCount)
		jsCountLine += lineCount
	print "\njs 代码 总计: %d" % jsCountLine

	cppCountLine = 0
	cpp_srcList = statistics_cpp_line(classes_root)
	for filename, lineCount in cpp_srcList:
		# print "%s - %d" % (filename, lineCount)
		cppCountLine += lineCount
	print "\ncpp 代码 总计: %d" % cppCountLine

	pass
	





