FROM docker-registry.s.arkea.com/arkea/java8adoptopenjdk

RUN yum update -y \
 && yum upgrade -y \
 && yum install -y unzip bzip2 python3 python36-lxml perl-XML-XPath libxml2 git \
 && yum clean all \
 && rm -rf /var/cache/yum

# Config gradle properties & proxy curl
# les lignes kapt.*** sont présentes suite à ce problème : https://youtrack.jetbrains.com/issue/KT-40750#focus=Comments-27-4815854.0-0
RUN mkdir ~/.gradle &&  cd ~/.gradle \
 && echo "systemProp.http.proxyHost=proxy-lb.gicm.net" >> gradle.properties \
 && echo "systemProp.http.proxyPort=3128" >> gradle.properties \
 && echo "systemProp.https.proxyHost=proxy-lb.gicm.net" >> gradle.properties \
 && echo "systemProp.https.proxyPort=3128" >> gradle.properties \
 && echo "org.gradle.daemon=false" >> gradle.properties \
 && echo "org.gradle.jvmargs=-Xms4g" >> gradle.properties \
 && echo "org.gradle.jvmargs=-Xmx6g" >> gradle.properties \
 && echo "org.gradle.workers.max=4" >> gradle.properties \
 && echo "arkeaUser=hudson" >> gradle.properties \
 && echo "arkeaPassword=hudson" >> gradle.properties \
 && echo "kapt.use.worker.api=false" >> gradle.properties \
 && echo "kapt.incremental.apt=false" >> gradle.properties \
 && echo "proxy = http://proxy-lb.gicm.net:3128" >> ~/.curlrc

# Download and install Kotlin compiler
# https://github.com/JetBrains/kotlin/releases/latest
ARG KOTLIN_VERSION=1.4.32
RUN cd /opt \
 && curl -LO https://github.com/JetBrains/kotlin/releases/download/v${KOTLIN_VERSION}/kotlin-compiler-${KOTLIN_VERSION}.zip \
 && unzip kotlin-compiler-${KOTLIN_VERSION}.zip \
 && rm -f kotlin-compiler-${KOTLIN_VERSION}.zip

# Code formating
RUN curl -sSLO https://github.com/pinterest/ktlint/releases/download/0.37.2/ktlint \
 && chmod 755 ktlint \
 && mv ktlint /usr/local/bin/

# Set the environment variables
ENV JAVA_HOME /opt/java8
ENV KOTLIN_HOME /opt/kotlinc

# Download and install Android SDK
# https://developer.android.com/studio#command-tools
ARG ANDROID_SDK_VERSION=6609375
ENV ANDROID_SDK_ROOT /opt/android-sdk
ENV PATH ${PATH}:${KOTLIN_HOME}/bin:${ANDROID_SDK_ROOT}/cmdline-tools/tools/bin:${ANDROID_SDK_ROOT}/platform-tools:${ANDROID_SDK_ROOT}/emulator:${JAVA_HOME}/bin
# WORKAROUND: for issue https://issuetracker.google.com/issues/37137213
ENV LD_LIBRARY_PATH ${ANDROID_SDK_ROOT}/emulator/lib64:${ANDROID_SDK_ROOT}/emulator/lib64/qt/lib
# patch emulator issue: Running as root without --no-sandbox is not supported. See https://crbug.com/638180.
# https://doc.qt.io/qt-5/qtwebengine-platform-notes.html#sandboxing-support
ENV QTWEBENGINE_DISABLE_SANDBOX 1
# Install SDK Android
ADD license_accepter.sh /opt/
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools \
 && cd /opt \
 && curl -LO https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip \
 && unzip commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip -d ${ANDROID_SDK_ROOT}/cmdline-tools \
 && rm -f commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip \
 && mkdir ~/.android \
 && touch ~/.android/repositories.cfg \
 && chmod 755 /opt/license_accepter.sh \
 && /opt/license_accepter.sh $ANDROID_SDK_ROOT

# Install android sdk modules
RUN sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "patcher;v4" \
 && sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "emulator" \
 && sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "platform-tools" \
 && sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "tools" \
 && sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "build-tools;28.0.3" \
 && sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "build-tools;29.0.2" \
 && sdkmanager --no_https --proxy_host="proxy-lb.gicm.net" --proxy_port="3128" --proxy=http --install "platforms;android-29"

# Add coverage
# https://docs.gitlab.com/ee/user/project/merge_requests/test_coverage_visualization.html
# https://gitlab.com/haynes/jacoco2cobertura
ADD cover2cover.py /opt/
ADD source2filename.py /opt/
RUN chmod +x /opt/*.py

# Create debug keystore for demo modules
RUN keytool -genkey -v -keystore ~/.android/debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 \
-dname "CN=GitlabCI, OU=Phenix, O=Arkea, L=Brest, ST=Bretagne, C=FR" \
-noprompt
