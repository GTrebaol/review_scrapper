
# 
# ReleaseNote
#
# Release not class are used to generate a changelog beetween two app or module version 
# This file automatically inspect dependencies beetween the 2 versions/branches and also generate a diff beetween all dependencies commits.
#
# HOW TO ruby -r "./fastlane/ReleaseNote.rb" -e "ReleaseNote.new.mainCoreApp"
# HOW TO ruby -r "./fastlane/ReleaseNote.rb" -e "ReleaseNote.new.mainModules"
#

require 'json'
require 'yaml'
require 'ostruct'

class ReleaseNote

    def initialize
        @baseRepoURL = "https://gitlark.s.arkea.com"
    end

    def saveFileContent(file)
        savedContent = ""
        File.foreach(file) { |line| savedContent += line }
        return savedContent
    end

    def parseFileProperties(file, property)
        File.foreach(file) { |line| 
            if (line.include? property)
                return line.split("=")[1].strip
            end
        }
        return ""
    end
 
    #
    # Get the last merge commit sha, will be use for git log commands
    #
    def getLastMergeCommitSha() 
        return `git log --merges  --pretty=format:"%h" -2 | tail -1`
    end

    def findGitlabProjectUrl(gitlabGroupId, dependency) 
        gitlabWriteUser = ENV["KS501_WRITE_USERNAME"]
        gitlabWriteToken = ENV["KS501_WRITE_TOKEN"]
        extractedPrefix = dependency.sub("_", " ").gsub("_", "-").split(" ")
        prefix = extractedPrefix[0].downcase
        research = extractedPrefix[1].downcase

        gitBaseUrl = transformURL("https://gitlark.s.arkea.com")

        puts("Searching #{research} into #{gitBaseUrl} with gitlabGroupId = #{gitlabGroupId} and prefix = #{prefix}...")

        proxy = ENV["HTTP_PROXY"].nil? ? "" : "-x #{ENV["HTTP_PROXY"]}" 
        researchResult = `curl #{proxy} -s --header "PRIVATE-TOKEN: #{gitlabWriteToken}" "#{gitBaseUrl}/api/v4/groups/#{gitlabGroupId}/projects?include_subgroups=true&archived=false&search=#{research}"`

        json = JSON.parse(researchResult)
        json.each do |jsonObject|
            if jsonObject["http_url_to_repo"].include? "#{prefix}"
                return transformURL(jsonObject["http_url_to_repo"])
            end
        end

        return nil
    end

    def transformURL(url) 
        bitrise = ENV["Bitrise"].nil? == false
        gitlabWriteUser = ENV["KS501_WRITE_USERNAME"]
        gitlabWriteToken = ENV["KS501_WRITE_TOKEN"]
        if bitrise 
            return url.gsub("https://gitlark.s.arkea.com", "https://#{gitlabWriteUser}:#{gitlabWriteToken}@gitlab-proxy.arkea.com/bitrise")
        else
            return url.gsub("https://gitlark.s.arkea.com", "https://#{gitlabWriteUser}:#{gitlabWriteToken}@gitlark.s.arkea.com")
        end
    end

    def generateDependenciesDiff()
        addedDependenciesDiff = `git diff #{getLastMergeCommitSha()}..HEAD buildSrc/src/main/kotlin/Dependencies.kt | egrep "const val" | egrep "^[+]" | sed 's/const val //;s/^.//'`
        deletedDependenciesDiff = `git diff #{getLastMergeCommitSha()}..HEAD buildSrc/src/main/kotlin/Dependencies.kt | egrep "const val" | egrep "^[-]" | sed 's/const val //;s/^.//'`
       
        addedDependencies = []
        addedDependenciesDiff.each_line do |dependency|
            project = dependency.strip.split("=")[0]
            version = dependency.strip.split("=")[1]
            addedDependencies.append(Dependency.new(project, version))
        end
        deletedDependencies = []
        deletedDependenciesDiff.each_line do |dependency|
            project = dependency.strip.split("=")[0]
            version = dependency.strip.split("=")[1]
            deletedDependencies.append(Dependency.new(project, version))
        end

        return addedDependencies.concat(deletedDependencies.reject {|dep| addedDependencies.find {|it| it.name == dep.name}.nil?}).group_by {|filterDep| filterDep.name}
    end

    # Generate the changelog for the current project (not dependencies)
    # - Parameter source: The source branch (ex: release)
    # - Parameter destination: The destination branch (ex: master)
    # If not branches are specifed release and master are the default choise
    def generateGitLog(folder, from, to)
        diff = if from.nil? == false 
            "#{from}..#{to}" 
        else 
            to 
        end
        
        changelog = `cd #{folder} && git log #{diff} --author-date-order --pretty=format:"%s" | grep -i -E -v "Merge|patch|auto"`
        return changelog
    end

    def generateRemoteCommitsDiff(url, projectName, dependencies)
        cleanDirectory()

        proxy = ENV["HTTP_PROXY"].nil? ? "" : "-c http.proxy=#{ENV["HTTP_PROXY"]}"

        `git #{proxy} clone #{transformURL(url)} tmp > /dev/null 2>&1`
       
        if ENV["LINUX_USER"].nil? == false
            `chown -R #{ENV["LINUX_USER"]} tmp`
        end
            
        targetVersion = dependencies[0].nil? ? nil : dependencies[0].version
        sourceVersion = dependencies[1].nil? ? nil : dependencies[1].version

        # Target version is mandatory to make a git log
        if targetVersion.nil? == false
    
            gitLog = generateGitLog("tmp", sourceVersion, targetVersion)
            if gitLog.empty? == false

                releaseNote = ""
                changelog = ""
                
                rn, cl = format_diff(gitLog, releaseNote, changelog)

                if rn.empty? == false
                    releaseNote = "## #{projectName}\n\n"
                    releaseNote += rn
                end
                if cl.empty? == false
                    changelog = "## #{projectName}\n\n"
                    changelog += cl
                end

                puts "[#{projectName}] changelog and release notes ✅"

                return releaseNote, changelog
            end
        end
    end

    # Format changelog
    # This function prevent remove duplicates in the given diff, detect JIRA issues and returns formatted issues links if possible
    def format_diff(diff, releaseNote, changelog)
        diff.each_line { |line| 
            match = line.match(/[A-Z]{2,10}-[0-9]{2,8}/m)
            puts "match = #{match}"

            if match != nil     
                link = "* [" + line.gsub("[", "\[").gsub("]", "\]").gsub("\n", "") + "]" + "(http://jira.intra.arkea.com:8080/jira/browse/#{match})\n"
                puts "link = #{link}"
                if !releaseNote.include?(link)
                    releaseNote += link
                elsif
                    puts "⏰ duplicate entry"
                end
            else 
                puts "line = #{line}"

                if line.include?("skip ci")
                    puts "⏰ Ignore skip ci commits"
                else
                    string = "* " + line
                    if !changelog.include?(string)
                        changelog += string
                    elsif
                        puts "⏰ duplicate entry"
                    end
                end
            end
        }
        
        return releaseNote, changelog
    end

    def cleanDirectory()
        `rm -rf tmp`
    end

    # Entry point for generating a release note.
    # - Parameter against: The source branch against which the diff is done (ex: master)
    # If no branches was specified current branche and master are the default choice.
    #
    def mainCoreApp()

        cleanDirectory()

        oldReleaseNote = saveFileContent("RELEASE_NOTES.md")
        newReleaseNote = ""
        oldChangelog = saveFileContent("CHANGELOG.md")
        newChangelog = ""

        versionName = parseFileProperties("gradle.properties", "PRODUCT_VERSION")

        newReleaseNote += "# [#{versionName}]\n\n"
        newChangelog += "# [#{versionName}]\n\n"
       
        # TODO USE TAGS
        gitLog = generateGitLog(".", getLastMergeCommitSha(), "HEAD")
        
        if gitLog.empty? == false
           coreReleaseNote, coreChangelog = format_diff(gitLog, "", "")
           newReleaseNote += "#{coreReleaseNote}\n"
           newChangelog += "#{coreChangelog}\n"
        end

        puts "[Coreapps] changelog and release notes ✅"

        generateDependenciesDiff().each do |k, v|

            url = findGitlabProjectUrl("2229", k)

            if url.nil?
                url = findGitlabProjectUrl("829", k)
            end

            if url.nil? == false
                releaseNote, changelog = generateRemoteCommitsDiff(url, k, v)
                if releaseNote.nil? == false && releaseNote.empty? == false
                    newReleaseNote += "#{releaseNote}\n"
                end
                if changelog.nil? == false && changelog.empty? == false
                    newChangelog += "#{changelog}\n"
                end
            end
        end

        newReleaseNote += oldReleaseNote
        newChangelog += oldChangelog

        File.write("RELEASE_NOTES.md", newReleaseNote)
        File.write("CHANGELOG.md", newChangelog)

        cleanDirectory()
        puts "[Coreapps] changelog and release notes fully completed ✅"
    end

    def mainModule()

        cleanDirectory()

        oldReleaseNote = saveFileContent("RELEASE_NOTES.md")
        newReleaseNote = ""
        oldChangelog = saveFileContent("CHANGELOG.md")
        newChangelog = ""

        versionName = parseFileProperties("gradle.properties", "VERSION_NAME")
        if versionName.nil?
            versionName = parseFileProperties("build.gradle.kts", "project.version")
        end

        newReleaseNote += "# [#{versionName}]\n\n"
        newChangelog += "# [#{versionName}]\n\n"

        # TODO USE TAGS
        gitLog = generateGitLog(".", getLastMergeCommitSha(), "HEAD")
        
        if gitLog.empty? == false
           coreReleaseNote, coreChangelog = format_diff(gitLog, "", "")

           if coreReleaseNote.empty? == false
                newReleaseNote += "#{coreReleaseNote}\n"
           else
                newReleaseNote += "No jiras for this versions\n\n"
           end

           if coreChangelog.empty? == false
                newChangelog += "#{coreChangelog}\n"
            else
                newChangelog += "No commit for this versions\n\n"
            end
        end

        newReleaseNote += oldReleaseNote
        newChangelog += oldChangelog

        File.write("RELEASE_NOTES.md", newReleaseNote)
        File.write("CHANGELOG.md", newChangelog)
    end
end

# Simple model object that represent a dependency
class Dependency
    attr_accessor :name, :version, :repo
    def initialize(name, version) 
        @name = name
        @version = version
    end
end