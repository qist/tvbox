<?php 
//管理员应急工具箱
error_reporting(E_ALL^E_NOTICE^E_WARNING^E_DEPRECATED);
define('DIR',dirname(__DIR__));
define('config_path', DIR . '/data/ATool_config.php'); ;

//判断配置文件是否存在
if(is_file(config_path)){
    require config_path;
    if(empty($config['key'])){
        exit('未读取到Key');
    }
    require DIR."/system/Msg.php";
}else{
    require DIR.'/system/public.php';
    Reset_Config();
}

//switch状态
if($config['switch'] === 1){
    
}else{
    $msg['title'] = 'ATool未开启';
    $msg['methodTitle'] = '开启方式:';
    $msg['content'] = '1. 登录您的云服务器或虚拟主机<br /> 2. 进入TwoNav的程序目录<br /> 3. 编辑 data/ATool_config.php 将"switch" => 0 改为 "switch" => 1 <br /> 4. 复制Key的内容,保存后刷新此页面,使用Key验证即可进入ATool';
    require DIR.'/templates/admin/other/error.php';
    exit;
}

session_name('ATool_SSID');
session_start();

if(!empty($_GET['type'])){
    if($_GET['type'] == 'verify'){
        if(isset($_SESSION['verify']) && $_SESSION['verify'] === true){
            msg(-1,'您已经验证过了,无需重复验证!');
        }else{
            if(!empty($_POST['Key']) && $_POST['Key'] === md5($config['key'])){
                $_SESSION['verify'] = true;
                msg(1,'验证成功');
            }else{
                msg(-1,'Key错误');
            }
        }
    }
    
    //判断是否已验证
    if(isset($_SESSION['verify']) && $_SESSION['verify'] === true){
        $db = Load_db();
        $global_config = unserialize( get_db("global_config", "v", ["k" => "o_config"]) );
    }else{
        msg(-1,'鉴权失败');
    }

    if($_GET['type'] == 'logout'){
        $_SESSION['verify'] = false;
        Reset_Config();
        msg(1,'退出成功');
    }elseif($_GET['type'] == 'user_list'){
        $query  = $_POST['query'];
        $UserGroup  = @$_POST['UserGroup'];
        $page   = empty(intval($_REQUEST['page'])) ? 1 : intval($_REQUEST['page']);
        $limit  = empty(intval($_REQUEST['limit'])) ? 50 : intval($_REQUEST['limit']);
        $offset = ($page - 1) * $limit; //起始行号
        //用户组筛选
        if(!empty($UserGroup)){
            $where['AND']['UserGroup'] = $UserGroup;
        }
        //关键字筛选
        if(!empty($query)){
            $where['AND']['OR'] = ["User[~]" => $query,"Email[~]" => $query,"RegIP[~]" => $query];
        }
        //统计条数
        $count = count_db('global_user',$where);
        //权重排序(数字小的排前面)
        $where['ORDER']['RegTime'] = 'DESC';
        //分页
        $where['LIMIT'] = [$offset,$limit];
        //查询
        $datas = select_db('global_user',['ID','User','UserGroup','Email','RegIP','RegTime','Login'],$where);
        if(!empty($datas)){
           $user_group = select_db('user_group',['name','code'],'');//读用户组
           $user_group = array_column($user_group, 'name', 'code');//以代号为键
           $user_group['root'] = '站长';
           $user_group['default'] = '默认';
           foreach ($datas as $key => $data){
               $datas[$key]['UserGroupName'] = $user_group[$data['UserGroup']]??'Null';
           }
        }
        msgA(['code'=>1,'msg'=>'获取成功','count'=>$count,'data'=>$datas]);
    }elseif($_GET['type'] == 'set_pwd'){
        if(!has_db('global_user',['ID'=>$_POST['ID']])){
            msg(-1,'用户不存在!');
        }
        //空字符串md5 防止意外出现空密码
        if( $_POST['new_pwd']== 'd41d8cd98f00b204e9800998ecf8427e'){
            msg(-1,'密码不能为空');
        }
        $RegTime = get_db('global_user','RegTime',['ID'=>$_POST['ID']]);
        update_db('global_user',['Password'=>Get_MD5_Password($_POST['new_pwd'],$RegTime)],["ID" => $_POST['ID'] ],[1,'修改成功']);
    }elseif($_GET['type'] == 'set_root'){
        update_db('global_user',['UserGroup'=>'root'],["ID" => $_POST['ID'] ],[1,'修改成功']);
    //设为允许注册
    }elseif($_GET['type'] == 'set_allow_register'){
        $global_config['RegOption'] = 1;
        update_db("global_config", ["v" => $global_config], ["k" => "o_config"],[1,'设置成功']);
    //关闭维护模式
    }elseif($_GET['type'] == 'set_close_Maintenance'){
        $global_config['Maintenance'] = 0;
        update_db("global_config", ["v" => $global_config], ["k" => "o_config"],[1,'设置成功']);
    //重置静态路径
    }elseif($_GET['type'] == 'Set_Libs'){
        $global_config['Libs'] = "./static";
        update_db("global_config", ["v" => $global_config], ["k" => "o_config"],[1,'设置成功']);
    //清理缓存
    }elseif($_GET['type'] == 'Set_clear_cache'){
        clearstatcache();
        if(function_exists("opcache_reset")){
            opcache_reset(); //清理PHP缓存
        }
        msgA(['code'=>1,'msg'=>'操作成功']);
    //改账号
    }elseif($_GET['type'] == 'set_user_name'){
        //新用户名是否合规
        if(empty($_POST['new_user_name'])){
            msgA(['code'=>-1,'msg'=>'用户名不能为空']);
        }elseif(empty($_POST['ID'])){
            msgA(['code'=>-1,'msg'=>'ID不能为空']);
        }elseif(!preg_match('/^[A-Za-z0-9]{4,13}$/',$_POST['new_user_name'])){
            msg(-1,'账号只能是4到13位的数字和字母!');
        }
        
        //检测是否冲突
        if(file_exists(DIR."/data/user/".$_POST['new_user_name'])){
            msgA(['code'=>-1,'msg'=>'data/user/存在同名文件夹']);
        }
        if(file_exists(DIR."/data/backup/".$_POST['new_user_name'])){
            msgA(['code'=>-1,'msg'=>'data/backup/存在同名文件夹']);
        }
        //读取用户信息
        $USER = get_db("global_user", "*", ["ID" => $_POST['ID']]);
        if(empty($USER)){
            msgA(['code'=>-1,'msg'=>'用户ID不存在']);
        }elseif($USER['User'] == $_POST['new_user_name']){
            msgA(['code'=>-1,'msg'=>'新用户名不能和旧的一样']);
        }elseif(has_db('global_user',['User'=>$_POST['new_user_name']])){
            msgA(['code'=>-1,'msg'=>'新账号已存在,请核对后再试!']);
        }
        //移动数据目录
        $Path = DIR.'/data/user/'.$USER['User'];
        if(is_dir($Path)){
            $New_Path = DIR.'/data/user/'.$_POST['new_user_name'];
            if(!rename($Path,$New_Path)){
                msgA(['code'=>-1,'msg'=>'移动数据目录失败']);
            }
        }
        //移动备份目录
        $Path = DIR.'/data/backup/'.$USER['User'];
        if(is_dir($Path)){
            $New_Path = DIR.'/data/backup/'.$_POST['new_user_name'];
            if(!rename($Path,$New_Path)){
                msgA(['code'=>-1,'msg'=>'移动备份目录失败']);
            }
        }
        update_db("user_login_info", ["user" => $_POST['new_user_name']], ["user" => $USER['User']]);
        update_db("user_log", ["user" => $_POST['new_user_name']], ["user" => $USER['User']]);
        update_db("global_user", ["User" => $_POST['new_user_name']], ["ID" => $_POST['ID']],[1,'操作成功']);
    }elseif($_GET['type'] == 'del_otp'){
        $user_data = get_db('global_user','*',['ID'=>$_POST['ID']]);
        $LoginConfig = unserialize($user_data['LoginConfig']);
        if(empty($LoginConfig['totp_key'])){
            msgA(['code'=>-1,'msg'=>'当前账号未开启OTP双重验证']);
        }
        $LoginConfig['totp_key'] = '';
        update_db("global_user", ["LoginConfig" => $LoginConfig], ["ID" => $_POST['ID']],[1,'操作成功']);
    }
    
    msgA(['code'=>-1,'msg'=>'请求类型错误']);
}else{
    //判断是否已验证
    if(isset($_SESSION['verify']) && $_SESSION['verify'] === true){
        $db = Load_db();
        $global_config = unserialize( get_db("global_config", "v", ["k" => "o_config"]) );
        echo_Atool();
    }else{
        echo_verify();
    }
}



//载入数据库
function Load_db(){
    require DIR."/data/config.php";
    require DIR.'/system/Medoo.php';
    if($db_config['type'] == 'sqlite'){
        try {
            $db_config['path'] = DIR."/data/".$db_config['file'];
            $db = new Medoo\Medoo(['type'=>'sqlite','database'=>$db_config['path']]);
        }catch (Exception $e) {
            Amsg(-1,'载入数据库失败'.$db_config['path']); 
        }
    }elseif($db_config['type'] == 'mysql'){
        try {
            $db = new Medoo\Medoo(['type' => 'mysql',
                'host' => $db_config['host'],
                'port' => $db_config['port'],
                'database' => $db_config['name'],
                'username' => $db_config['user'],
                'password' => $db_config['password']
            ]);
        }catch (Exception $e) {
            Amsg(-1,'链接数据库失败!'); 
        }
    }
    require DIR.'/system/public.php';
    return $db;
}

function echo_Atool(){ 
    global $global_config;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ATool 工具箱</title>
    <link rel="stylesheet" href="../static/Layui/v2.8.17/css/layui.css">
    <style>
        html, body {min-width: 1200px;background-color: #fff;position: relative;}
        .page-wrapper {width: 1200px;margin: 0 auto;padding: 0 15px;}
    </style>
</head>
<body>
<div class="page-wrapper">
    <fieldset class="layui-elem-field layui-field-title">
        <legend> ATool 工具箱 </legend>
    </fieldset>
    <div class="layui-btn-container" style="display: inline-block;">
        <button id="logout" class="layui-btn layui-btn-sm layui-btn-primary"><i class="layui-icon layui-icon-snowflake"></i>安全退出</button>
        <a class="layui-btn layui-btn-sm layui-btn-primary" href="../index.php?c=<?php echo $global_config['Login'];?>" target="_blank"><i class="layui-icon layui-icon-username"></i>打开登录页</a>
        <a class="layui-btn layui-btn-sm layui-btn-primary" href="../index.php?c=<?php ec