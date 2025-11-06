네, 좋습니다. rqtcontroller라는 이름의 패키지를 기준으로, 순수 PyQt5 코드로 빈 창을 띄우는 rqt 플러그인을 만드는 데 필요한 모든 파일의 전체 내용을 다시 작성해 드립니다.
📂 1. 전체 파일 구조
먼저, ~/ros2_ws/src/rqtcontroller 패키지 내부의 파일 구조는 다음과 같아야 합니다.
rqtcontroller/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── rqtcontroller.xml
└── rqtcontroller/
    ├── __init__.py
    └── controller_plugin.py  (플러그인 로직)

✍️ 2. 파일별 전체 내용
각 파일을 아래 내용으로 복사하여 붙여넣거나 수정하세요.
📄 package.xml
 * rqt_gui, rqt_gui_py 의존성을 추가합니다.
 * <export> 태그에 .xml 확장자를 포함한 정확한 경로를 지정합니다.
<!-- end list -->
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>rqtcontroller</name>
  <version>0.0.0</version>
  <description>A simple rqt plugin created with pure PyQt5.</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <depend>rqt_gui</depend>
  <depend>rqt_gui_py</depend>
  <exec_depend>python3-pyqt5</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <rqt_gui plugin="${prefix}/resource/rqtcontroller.xml"/>
  </export>
</package>

📄 setup.py
 * data_files 항목에 .xml 확장자를 포함한 정확한 파일 경로를 지정합니다.
 * entry_points에 플러그인 클래스 경로를 정확히 지정합니다. (패키지명.모듈명:클래스명)
<!-- end list -->
from setuptools import setup

package_name = 'rqtcontroller'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # [수정 완료] .xml 확장자를 포함한 정확한 경로
        ('share/' + package_name + '/resource',
            ['resource/rqtcontroller.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='A simple rqt plugin created with pure PyQt5.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
        # [중요] rqt 플러그인 진입점
        # ID 'rqtcontroller' = rqtcontroller/controller_plugin.py 안의 ControllerPlugin 클래스
        'rqt_gui.py': [
            'rqtcontroller = rqtcontroller.controller_plugin:ControllerPlugin',
        ],
    },
)

📄 setup.cfg
 * Python 스크립트의 설치 경로를 지정합니다.
<!-- end list -->
[develop]
script_dir=$base/lib/rqtcontroller
[install]
install_scripts=$base/lib/rqtcontroller

📄 resource/rqtcontroller.xml
 * resource 폴더 안에 이 파일을 생성해야 합니다.
 * <library path="...">의 path 값은 setup.py의 entry_points에서 사용한 ID(rqtcontroller)와 일치해야 합니다.
 * <class type="...">의 type 값은 setup.py의 entry_points에서 사용한 클래스 경로(rqtcontroller.controller_plugin:ControllerPlugin)와 일치해야 합니다.
<!-- end list -->
<library path="rqtcontroller">
  <class name="My Controller Plugin" 
         type="rqtcontroller.controller_plugin.ControllerPlugin" 
         base_class_type="rqt_gui_py.plugin.Plugin">
    <description>
      PyQt5 코드로만 만든 컨트롤러 플러그인입니다.
    </description>
    <qtgui>
      <group>
        <label>My Plugins</label>
      </group>
      <label>Controller Plugin</label>
      <icon type="theme">applications-other</icon>
      <statustip>PyQt5 컨트롤러 플러그인을 엽니다.</statustip>
    </qtgui>
  </class>
</library>

📄 rqtcontroller/__init__.py
 * 이 파일은 rqtcontroller 폴더(파이썬 소스 코드 폴더) 내부에 있어야 합니다.
 * 내용은 비어 있어도 됩니다. Python이 이 폴더를 패키지로 인식하도록 합니다.
<!-- end list -->
# 이 파일은 비워둡니다.

📄 rqtcontroller/controller_plugin.py
 * rqtcontroller 폴더 내부에 생성합니다.
 * 실제 플러그인의 로직이 담긴 파일입니다.
<!-- end list -->
import os
from qt_core.qt_compat import qt_api # rqt의 Qt 호환성 모듈
from rqt_gui_py.plugin import Plugin
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton # PyQt5 위젯 사용

class ControllerPlugin(Plugin):

    def __init__(self, context):
        """
        플러그인 초기화
        """
        super(ControllerPlugin, self).__init__(context)
        
        # 플러그인 객체 이름 설정
        self.setObjectName('ControllerPlugin')

        # [핵심] UI 파일을 로드하는 대신, QWidget을 직접 생성합니다.
        self._widget = QWidget()
        
        # UI 요소(레이아웃, 라벨, 버튼)를 코드로 직접 생성
        layout = QVBoxLayout()
        info_label = QLabel("rqtcontroller 플러그인이 로드되었습니다.\n(순수 PyQt5 코드)")
        test_button = QPushButton("로그 출력 버튼")
        
        # 레이아웃에 위젯 추가
        layout.addWidget(info_label)
        layout.addWidget(test_button)
        
        # 메인 위젯(_widget)에 레이아웃 적용
        self._widget.setLayout(layout)

        # rqt GUI에 우리가 만든 메인 위젯을 추가
        context.add_widget(self._widget)

        # 버튼 클릭 시그널에 _on_button_click 함수 연결
        test_button.clicked.connect(self._on_button_click)

    def _on_button_click(self):
        # rqt 플러그인은 self.get_logger()를 통해 ROS 2 로거를 사용할 수 있습니다.
        self.get_logger().info("ControllerPlugin 버튼 클릭!")

    def shutdown_plugin(self):
        """
        플러그인 종료 시 호출 (필수)
        """
        self.get_logger().info("ControllerPlugin을 종료합니다.")
        # TODO: 여기서 ROS 구독자, 퍼블리셔 등을 정리합니다.
        pass

    def save_settings(self, plugin_settings, instance_settings):
        """
        설정 저장 (필수)
        """
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        """
        설정 복원 (필수)
        """
        pass

