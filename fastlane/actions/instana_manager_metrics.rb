module Fastlane
    module Actions
      class InstanaManagerAction < Action
        def self.run(params)
          app_name = params[:app_name]
          timeframe = params[:timeframe]
          data_type = params[:data_type]
          production = params[:production]
          instana_manager_cmd = "python3 #{ENV["PWD"]}/fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/mobile.git/fastlane/scripts/instana_manager/instana_manager.py"
          if production
            instana_manager_cmd << "\s-p"
          end
          instana_manager_cmd << "\s--data #{data_type} #{app_name} #{timeframe}"
          sh(instana_manager_cmd)
        end

        def self.description
          "Fetch metrics of a mobile app on Instana."
        end

        def self.authors
          ["Ops Distri Mobile"]
        end

        def self.details
          "Fetch metrics of a mobile app on Instana."
        end

        def self.available_options
          [
            FastlaneCore::ConfigItem.new(key: :app_name,
                        env_name: "MOBILE_TOOLS_INSTANA_APP_NAME",
                     description: "The name of the application",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :timeframe,
                        env_name: "MOBILE_TOOLS_INSTANA_TIMEFRAME",
                     description: "Timeframe of the wanted data in MS",
                        optional: false,
                            type: String),
            FastlaneCore::ConfigItem.new(key: :data_type,
                        env_name: "MOBILE_TOOLS_INSTANA_DATA_TYPE",
                     description: "Type of data wanted, only crash_list atm",
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
