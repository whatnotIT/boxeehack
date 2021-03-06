import time
import os,sys
import xbmc, xbmcgui, mc
import subprocess

os.environ["LD_LIBRARY_PATH"]=".:/data/hack/lib:/opt/local/lib:/usr/local/lib:/usr/lib:/lib:/lib/gstreamer-0.10:/opt/local/lib/qt"

def set_watched(command):
	list = mc.GetWindow(10483).GetList(52)
	item = list.GetItem(1)

	series = mc.GetInfoString("Container(52).ListItem.TVShowTitle")
	db_path = xbmc.translatePath('special://profile/Database/')
	itemList = list.GetItems()
	seasons = []
	episodes_count = 0
	for item in itemList:
		season = item.GetSeason()
		if(season != -1):
			seasons.append(season)
			episodes_count = episodes_count + 1

	seasons = dict.fromkeys(seasons)
	seasons = seasons.keys()

	use_season = -1
	display_name = series
	season_string = ""
	if(len(seasons) == 1):
		display_name = "Season %s" % (seasons[0])
		season_string = " %s" % display_name
		use_season = seasons[0]

	dialog = xbmcgui.Dialog()
    	if dialog.yesno("Watched", "Do you want to mark all episodes of %s%s as %s?" % (series, season_string, command)):
        	progress = xbmcgui.DialogProgress()
        	progress.create('Updating episodes', 'Setting %s%s as %s' % (series, season_string, command))

		current_count = 0
		info_count = 0

		sql = ".timeout 100000;\n"
				
		for item in itemList:
			episode = item.GetEpisode()
			boxeeid = mc.GetInfoString("Container(52).ListItem("+str(info_count)+").Property(boxeeid)")
			info_count = info_count + 1
			print boxeeid
			if(episode != -1):
				current_count = current_count+1
				percent = int( ( episodes_count / current_count ) * 100)
				message = "Episode " + str(current_count) + " out of " + str(episodes_count)
				progress.update( percent, "", message, "" )
				path = item.GetPath()

				# First make sure we don't get double values in the DB, so remove any old ones				
				sql = sql + "DELETE FROM watched WHERE strPath = \""+path+"\" or (strBoxeeId != \"\" AND strBoxeeId = \""+boxeeid+"\");\n"
				if command == "watched":
					sql = sql + "INSERT INTO watched VALUES(null, \""+path+"\", \""+boxeeid+"\", 1, 0, -1.0);\n"

		file_put_contents("/tmp/sqlinject", sql)
		os.system('cat /tmp/sqlinject | /data/hack/bin/sqlite3 ' + db_path + 'boxee_user_catalog.db')

		xbmc.executebuiltin("Container.Update")
		xbmc.executebuiltin("Container.Refresh")
		xbmc.executebuiltin("Window.Refresh")
		progress.close()

		xbmc.executebuiltin("XBMC.ReplaceWindow(10483)")

#        	progress = xbmcgui.DialogProgress()
#        	progress.create('Updating episodes', 'Setting %s%s as %s' % (series, season_string, command))
#
#		for x in range(0, 10):
#			time.sleep(1);
#			xbmc.executebuiltin("Container.Update")
#			xbmc.executebuiltin("Container.Refresh")
#			xbmc.executebuiltin("Window.Refresh")
#
#		progress.close()
#
#		xbmc.executebuiltin("XBMC.ReplaceWindow(10483)")

		xbmc.executebuiltin("Notification(,%s marked as %s...,2000)" % (display_name, command))

def file_put_contents(filename, content):
	fp = open(filename, "w")
	fp.write(content)
	fp.close()

if (__name__ == "__main__"):
    	command = sys.argv[1]
	set_watched(command)
