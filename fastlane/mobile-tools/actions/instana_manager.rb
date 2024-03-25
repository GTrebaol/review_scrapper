module Fastlane
    module Actions
      class InstanaManagerAction < Action
        def self.run(params)
          os = params[:os]
          working_dir = params[:working_dir]
          file_name = params[:file_name]
          file_id = params[:file_id]
          config_id = params[:config_id]
          sourcemap_upload_id = params[:sourcemap_upload_id]
          production = params[:production]
          instana_manager_cmd = "python3 #{ENV["PWD"]}/fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/mobile.git/fastlane/mobile-tools/scripts/instana_manager/instana_manager.py"
          if production
            instana_manager_cmd << "\s-p"
          end
          if os == "ANDROID"
            instana_manager_cmd << "\s-ua #{working_dir} #{file_name} #{file_id} #{config_id} #{sourcemap_upload_id}"
          else
            instana_manager_cmd << "\s-ui #{working_dir} #{file_name} #{file_id} #{config_id} #{sourcemap_upload_id}"
          end
          sh(instana_manager_cmd)
        end
  
        def self.description
          "Publish crash files on Instana."
        end
  
        def self.authors
          ["DO Mobile"]
        end
    
        def self.details
          "Publish crash files on Instana."
        end

        def self.available_options
          [
            FastlaneCore::ConfigItem.new(key: :os,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_OS",
                     description: "The OS of the application",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :working_dir,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_WORKING_DIR",
                     description: "The working dir where the symbols are",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :file_name,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_FILE_NAME",
                     description: "The file name to upload",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :file_id,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_FILE_ID",
                     description: "The file ID to upload",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :config_id,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_CONFIG_ID",
                     description: "The config id where to upload files",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :sourcemap_upload_id,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_SOURCEMAP_UPLOAD_ID",
                     description: "The sourcemap id where to upload files",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :production,
                        env_name: "DO_MOBILE_TOOLS_INSTANA_PRODUCTION",
                      description: "Use the production instance of Instana",
                        optional: false,
                            type: Boolean),    
            ]
        end    
    
        def self.is_supported?(platform)
          true
        end
      end
    end
  end
  