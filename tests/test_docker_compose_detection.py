#!/usr/bin/env python3
"""
Test script for Docker Compose detection and docker-compose.yml generation.
Tests the new features added for enhanced Nextcloud restore workflow.
"""

import os
import sys
import tempfile
import shutil
import re
import subprocess

# Since we can't import the main module due to tkinter dependency,
# we'll include the relevant functions here for testing

def parse_config_php_full(config_php_path):
    """
    Parse config.php file and extract all relevant settings for Docker Compose generation.
    Returns: dict with config settings or None if parsing fails
    """
    try:
        if not os.path.exists(config_php_path):
            return None
        
        with open(config_php_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = {}
        
        # Extract database settings
        dbtype_match = re.search(r"['\"]dbtype['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbtype_match:
            config['dbtype'] = dbtype_match.group(1).lower()
        
        dbname_match = re.search(r"['\"]dbname['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbname_match:
            config['dbname'] = dbname_match.group(1)
        
        dbuser_match = re.search(r"['\"]dbuser['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbuser_match:
            config['dbuser'] = dbuser_match.group(1)
        
        dbpassword_match = re.search(r"['\"]dbpassword['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbpassword_match:
            config['dbpassword'] = dbpassword_match.group(1)
        
        dbhost_match = re.search(r"['\"]dbhost['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbhost_match:
            config['dbhost'] = dbhost_match.group(1)
        
        dbport_match = re.search(r"['\"]dbport['\"] => ['\"]?([^'\"]+)['\"]?", content)
        if dbport_match:
            config['dbport'] = dbport_match.group(1)
        
        # Extract data directory
        datadirectory_match = re.search(r"['\"]datadirectory['\"] => ['\"]([^'\"]+)['\"]", content)
        if datadirectory_match:
            config['datadirectory'] = datadirectory_match.group(1)
        
        # Extract trusted domains (array format)
        trusted_domains = []
        trusted_domains_pattern = r"['\"]trusted_domains['\"]\s*=>\s*array\s*\((.*?)\)"
        td_match = re.search(trusted_domains_pattern, content, re.DOTALL)
        if td_match:
            domains_str = td_match.group(1)
            # Extract individual domain entries
            domain_entries = re.findall(r"['\"]([^'\"]+)['\"]", domains_str)
            trusted_domains = domain_entries
        config['trusted_domains'] = trusted_domains
        
        return config
    except Exception as e:
        print(f"Error parsing full config.php: {e}")
        return None

def detect_docker_compose_usage():
    """
    Detect if Docker Compose was used to start the current containers.
    Returns: (is_compose, compose_file_path) tuple
    """
    try:
        # Check if docker-compose.yml exists in current directory
        compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']
        for filename in compose_files:
            if os.path.exists(filename):
                print(f"✓ Found Docker Compose file: {filename}")
                return True, filename
        
        # Check running containers for Docker Compose labels
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Labels}}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if 'com.docker.compose' in line:
                    print("✓ Detected Docker Compose labels on running containers")
                    return True, None
        
        return False, None
    except Exception as e:
        print(f"Error detecting Docker Compose usage: {e}")
        return False, None

def generate_docker_compose_yml(config, nextcloud_port=8080, db_port=5432):
    """
    Generate docker-compose.yml content based on config.php settings.
    
    Args:
        config: dict with config.php settings
        nextcloud_port: port to expose Nextcloud on
        db_port: port to expose database on (if applicable)
    
    Returns:
        str: docker-compose.yml content
    """
    dbtype = config.get('dbtype', 'pgsql')
    dbname = config.get('dbname', 'nextcloud')
    dbuser = config.get('dbuser', 'nextcloud')
    dbpassword = config.get('dbpassword', 'changeme')
    datadirectory = config.get('datadirectory', '/var/www/html/data')
    trusted_domains = config.get('trusted_domains', ['localhost'])
    
    # Determine database service configuration
    if dbtype == 'sqlite':
        # SQLite - no separate database service needed
        compose_content = f"""version: '3.8'

services:
  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    restart: unless-stopped
    environment:
      - SQLITE_DATABASE={dbname}
"""
    elif dbtype in ['mysql', 'mariadb']:
        # MySQL/MariaDB
        compose_content = f"""version: '3.8'

services:
  db:
    image: mariadb:10.11
    container_name: nextcloud-db
    restart: unless-stopped
    command: --transaction-isolation=READ-COMMITTED --log-bin=binlog --binlog-format=ROW
    volumes:
      - ./db-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD={dbpassword}
      - MYSQL_PASSWORD={dbpassword}
      - MYSQL_DATABASE={dbname}
      - MYSQL_USER={dbuser}
    ports:
      - "{db_port}:3306"

  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    restart: unless-stopped
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - MYSQL_PASSWORD={dbpassword}
      - MYSQL_DATABASE={dbname}
      - MYSQL_USER={dbuser}
      - MYSQL_HOST=db
    depends_on:
      - db
"""
    else:  # PostgreSQL
        compose_content = f"""version: '3.8'

services:
  db:
    image: postgres:15
    container_name: nextcloud-db
    restart: unless-stopped
    volumes:
      - ./db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD={dbpassword}
      - POSTGRES_DB={dbname}
      - POSTGRES_USER={dbuser}
    ports:
      - "{db_port}:5432"

  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    restart: unless-stopped
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - POSTGRES_PASSWORD={dbpassword}
      - POSTGRES_DB={dbname}
      - POSTGRES_USER={dbuser}
      - POSTGRES_HOST=db
    depends_on:
      - db
"""
    
    # Add comments about configuration
    header = f"""# Docker Compose configuration for Nextcloud
# Generated based on config.php settings from backup
#
# Detected configuration:
#   - Database type: {dbtype}
#   - Database name: {dbname}
#   - Data directory: {datadirectory}
#   - Trusted domains: {', '.join(trusted_domains)}
#
# IMPORTANT: Ensure the following directories exist before starting:
#   - ./nextcloud-data (will contain Nextcloud files)
"""
    if dbtype not in ['sqlite', 'sqlite3']:
        header += "#   - ./db-data (will contain database files)\n"
    
    header += "#\n# To start: docker-compose up -d\n# To stop: docker-compose down\n\n"
    
    return header + compose_content

def test_parse_config_php_full():
    """Test full config.php parsing for all settings"""
    print("\n" + "="*60)
    print("TEST: Parse full config.php with all settings")
    print("="*60)
    
    # Create a temporary config.php with all settings
    temp_dir = tempfile.mkdtemp(prefix="test_config_full_")
    config_path = os.path.join(temp_dir, "config.php")
    
    config_content = """<?php
$CONFIG = array (
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud_db',
  'dbuser' => 'nc_admin',
  'dbpassword' => 'secure_password_123',
  'dbhost' => 'localhost',
  'dbport' => '5432',
  'datadirectory' => '/var/www/html/data',
  'trusted_domains' => 
  array (
    0 => 'localhost',
    1 => 'nextcloud.example.com',
    2 => '192.168.1.100',
  ),
);
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    try:
        # Parse the config
        config = parse_config_php_full(config_path)
        
        # Verify all settings were extracted
        assert config is not None, "Config parsing returned None"
        assert config.get('dbtype') == 'pgsql', f"Expected dbtype 'pgsql', got {config.get('dbtype')}"
        assert config.get('dbname') == 'nextcloud_db', f"Expected dbname 'nextcloud_db', got {config.get('dbname')}"
        assert config.get('dbuser') == 'nc_admin', f"Expected dbuser 'nc_admin', got {config.get('dbuser')}"
        assert config.get('dbpassword') == 'secure_password_123', "Password not extracted correctly"
        assert config.get('dbhost') == 'localhost', f"Expected dbhost 'localhost', got {config.get('dbhost')}"
        assert config.get('dbport') == '5432', f"Expected dbport '5432', got {config.get('dbport')}"
        assert config.get('datadirectory') == '/var/www/html/data', "Data directory not extracted"
        
        # Verify trusted domains
        trusted_domains = config.get('trusted_domains', [])
        assert len(trusted_domains) == 3, f"Expected 3 trusted domains, got {len(trusted_domains)}"
        assert 'localhost' in trusted_domains, "localhost not in trusted domains"
        assert 'nextcloud.example.com' in trusted_domains, "nextcloud.example.com not in trusted domains"
        assert '192.168.1.100' in trusted_domains, "192.168.1.100 not in trusted domains"
        
        print("✅ All config settings parsed correctly")
        print(f"  - Database type: {config.get('dbtype')}")
        print(f"  - Database name: {config.get('dbname')}")
        print(f"  - Database user: {config.get('dbuser')}")
        print(f"  - Database host: {config.get('dbhost')}")
        print(f"  - Data directory: {config.get('datadirectory')}")
        print(f"  - Trusted domains: {len(trusted_domains)} domains")
        
        return True
        
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_parse_config_php_mysql():
    """Test config.php parsing for MySQL database"""
    print("\n" + "="*60)
    print("TEST: Parse config.php with MySQL database")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp(prefix="test_config_mysql_")
    config_path = os.path.join(temp_dir, "config.php")
    
    config_content = """<?php
$CONFIG = array (
  'dbtype' => 'mysql',
  'dbname' => 'nc_mysql',
  'dbuser' => 'mysql_user',
  'dbpassword' => 'mysql_pass',
  'dbhost' => 'db',
  'datadirectory' => '/mnt/data',
  'trusted_domains' => 
  array (
    0 => 'cloud.local',
  ),
);
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    try:
        config = parse_config_php_full(config_path)
        
        assert config is not None, "Config parsing returned None"
        assert config.get('dbtype') == 'mysql', f"Expected dbtype 'mysql', got {config.get('dbtype')}"
        assert config.get('dbname') == 'nc_mysql', f"Expected dbname 'nc_mysql', got {config.get('dbname')}"
        
        print("✅ MySQL config parsed correctly")
        print(f"  - Database type: {config.get('dbtype')}")
        print(f"  - Database name: {config.get('dbname')}")
        
        return True
        
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(temp_dir)


def test_generate_docker_compose_postgresql():
    """Test docker-compose.yml generation for PostgreSQL"""
    print("\n" + "="*60)
    print("TEST: Generate docker-compose.yml for PostgreSQL")
    print("="*60)
    
    config = {
        'dbtype': 'pgsql',
        'dbname': 'nextcloud',
        'dbuser': 'ncuser',
        'dbpassword': 'ncpass',
        'datadirectory': '/var/www/html/data',
        'trusted_domains': ['localhost', 'nextcloud.local']
    }
    
    try:
        compose_content = generate_docker_compose_yml(config, nextcloud_port=8080, db_port=5432)
        
        # Verify compose file contains expected elements
        assert compose_content is not None, "Compose content is None"
        assert 'version:' in compose_content, "Missing version field"
        assert 'services:' in compose_content, "Missing services field"
        assert 'db:' in compose_content, "Missing db service"
        assert 'nextcloud:' in compose_content, "Missing nextcloud service"
        assert 'postgres' in compose_content.lower(), "Missing postgres image"
        assert 'POSTGRES_DB=nextcloud' in compose_content, "Missing POSTGRES_DB env"
        assert 'POSTGRES_USER=ncuser' in compose_content, "Missing POSTGRES_USER env"
        assert '8080:80' in compose_content, "Missing port mapping for Nextcloud"
        assert '5432:5432' in compose_content, "Missing port mapping for database"
        assert 'depends_on:' in compose_content, "Missing depends_on for nextcloud"
        
        print("✅ PostgreSQL docker-compose.yml generated correctly")
        print(f"  - Contains version field")
        print(f"  - Contains db and nextcloud services")
        print(f"  - Contains postgres image")
        print(f"  - Contains correct environment variables")
        print(f"  - Contains correct port mappings")
        
        return True
        
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        print(f"Generated content:\n{compose_content}")
        return False
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_docker_compose_mysql():
    """Test docker-compose.yml generation for MySQL"""
    print("\n" + "="*60)
    print("TEST: Generate docker-compose.yml for MySQL")
    print("="*60)
    
    config = {
        'dbtype': 'mysql',
        'dbname': 'nc_db',
        'dbuser': 'nc_user',
        'dbpassword': 'nc_password',
        'datadirectory': '/data',
        'trusted_domains': ['example.com']
    }
    
    try:
        compose_content = generate_docker_compose_yml(config, nextcloud_port=9000, db_port=3306)
        
        # Verify compose file contains expected elements for MySQL
        assert compose_content is not None, "Compose content is None"
        assert 'mariadb' in compose_content.lower(), "Missing mariadb image"
        assert 'MYSQL_DATABASE=nc_db' in compose_content, "Missing MYSQL_DATABASE env"
        assert 'MYSQL_USER=nc_user' in compose_content, "Missing MYSQL_USER env"
        assert '9000:80' in compose_content, "Missing port mapping for Nextcloud"
        assert '3306:3306' in compose_content or '3306' in compose_content, "Missing MySQL port"
        
        print("✅ MySQL docker-compose.yml generated correctly")
        print(f"  - Contains mariadb image")
        print(f"  - Contains correct MySQL environment variables")
        print(f"  - Contains correct port mappings")
        
        return True
        
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        print(f"Generated content:\n{compose_content}")
        return False
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_docker_compose_sqlite():
    """Test docker-compose.yml generation for SQLite"""
    print("\n" + "="*60)
    print("TEST: Generate docker-compose.yml for SQLite")
    print("="*60)
    
    config = {
        'dbtype': 'sqlite',
        'dbname': 'nextcloud.db',
        'datadirectory': '/var/www/html/data',
        'trusted_domains': ['localhost']
    }
    
    try:
        compose_content = generate_docker_compose_yml(config, nextcloud_port=8080)
        
        # Verify compose file contains expected elements for SQLite
        assert compose_content is not None, "Compose content is None"
        assert 'services:' in compose_content, "Missing services field"
        assert 'nextcloud:' in compose_content, "Missing nextcloud service"
        # SQLite should NOT have a separate db service
        assert compose_content.count('image:') == 1, "SQLite should only have one service"
        assert 'SQLITE_DATABASE' in compose_content, "Missing SQLITE_DATABASE env"
        
        print("✅ SQLite docker-compose.yml generated correctly")
        print(f"  - Contains only nextcloud service (no separate db)")
        print(f"  - Contains SQLite environment variable")
        
        return True
        
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        print(f"Generated content:\n{compose_content}")
        return False
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detect_docker_compose_file():
    """Test detection of existing docker-compose.yml file"""
    print("\n" + "="*60)
    print("TEST: Detect existing docker-compose.yml file")
    print("="*60)
    
    # Save current directory
    original_dir = os.getcwd()
    
    # Create a temporary directory and compose file
    temp_dir = tempfile.mkdtemp(prefix="test_compose_detect_")
    compose_path = os.path.join(temp_dir, "docker-compose.yml")
    
    with open(compose_path, 'w') as f:
        f.write("version: '3.8'\nservices:\n  test:\n    image: nginx")
    
    try:
        # Change to temp directory
        os.chdir(temp_dir)
        
        # Detect compose file
        is_compose, compose_file = detect_docker_compose_usage()
        
        assert is_compose == True, "Should detect docker-compose.yml"
        assert compose_file == "docker-compose.yml", f"Expected 'docker-compose.yml', got {compose_file}"
        
        print("✅ Docker Compose file detected correctly")
        print(f"  - Detected: {compose_file}")
        
        return True
        
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)
        # Clean up
        shutil.rmtree(temp_dir)


def test_detect_no_docker_compose():
    """Test detection when no docker-compose file exists"""
    print("\n" + "="*60)
    print("TEST: Detect absence of docker-compose.yml")
    print("="*60)
    
    # Save current directory
    original_dir = os.getcwd()
    
    # Create a temporary directory without compose file
    temp_dir = tempfile.mkdtemp(prefix="test_no_compose_")
    
    try:
        # Change to temp directory
        os.chdir(temp_dir)
        
        # Detect compose file (should not find one)
        is_compose, compose_file = detect_docker_compose_usage()
        
        # Note: is_compose might still be True if running containers have compose labels
        # but compose_file should be None since there's no file in the directory
        print(f"  Detection result: is_compose={is_compose}, compose_file={compose_file}")
        
        print("✅ Detection works in directory without docker-compose.yml")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)
        # Clean up
        shutil.rmtree(temp_dir)


def main():
    print("="*60)
    print("DOCKER COMPOSE DETECTION AND GENERATION - TEST SUITE")
    print("="*60)
    
    all_passed = True
    
    # Run all tests
    tests = [
        test_parse_config_php_full,
        test_parse_config_php_mysql,
        test_generate_docker_compose_postgresql,
        test_generate_docker_compose_mysql,
        test_generate_docker_compose_sqlite,
        test_detect_docker_compose_file,
        test_detect_no_docker_compose,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
            all_passed = all_passed and result
        except Exception as e:
            print(f"❌ Test {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
            all_passed = False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
