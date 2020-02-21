# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Battotal(models.Model):
    pcode = models.CharField(db_column='PCODE', primary_key=True, max_length=5)  # Field name made lowercase.
    gyear = models.CharField(db_column='GYEAR', max_length=4)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hra = models.FloatField(db_column='HRA', blank=True, null=True)  # Field name made lowercase.
    gamenum = models.IntegerField(db_column='GAMENUM', blank=True, null=True)  # Field name made lowercase.
    ab = models.IntegerField(db_column='AB', blank=True, null=True)  # Field name made lowercase.
    run = models.IntegerField(db_column='RUN', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    h2 = models.IntegerField(db_column='H2', blank=True, null=True)  # Field name made lowercase.
    h3 = models.IntegerField(db_column='H3', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    tb = models.IntegerField(db_column='TB', blank=True, null=True)  # Field name made lowercase.
    rbi = models.IntegerField(db_column='RBI', blank=True, null=True)  # Field name made lowercase.
    sb = models.IntegerField(db_column='SB', blank=True, null=True)  # Field name made lowercase.
    cs = models.IntegerField(db_column='CS', blank=True, null=True)  # Field name made lowercase.
    sh = models.IntegerField(db_column='SH', blank=True, null=True)  # Field name made lowercase.
    sf = models.IntegerField(db_column='SF', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.
    kk = models.IntegerField(db_column='KK', blank=True, null=True)  # Field name made lowercase.
    gd = models.IntegerField(db_column='GD', blank=True, null=True)  # Field name made lowercase.
    err = models.IntegerField(db_column='ERR', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(db_column='SCORE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'battotal'
        unique_together = (('pcode', 'gyear'),)


class CancelGame(models.Model):
    gmkey = models.CharField(primary_key=True, max_length=13)
    gyear = models.SmallIntegerField()
    reason = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'cancel_game'
        unique_together = (('gmkey', 'gyear'),)


class DuplicateName(models.Model):
    name_view = models.CharField(db_column='NAME_VIEW', max_length=20, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=20)  # Field name made lowercase.
    pcode = models.CharField(db_column='PCODE', primary_key=True, max_length=5)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=255, blank=True, null=True)  # Field name made lowercase.
    position = models.CharField(db_column='POSITION', max_length=255, blank=True, null=True)  # Field name made lowercase.
    pos = models.CharField(db_column='POS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    birth = models.CharField(db_column='BIRTH', max_length=255, blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'duplicate_name'


class Entry(models.Model):
    gmkey = models.CharField(db_column='GMKEY', max_length=13)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR', primary_key=True)  # Field name made lowercase.
    gday = models.CharField(db_column='GDAY', max_length=8)  # Field name made lowercase.
    turn = models.CharField(db_column='TURN', max_length=2)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=15)  # Field name made lowercase.
    pcode = models.CharField(db_column='PCODE', max_length=10)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=1)  # Field name made lowercase.
    posi = models.CharField(db_column='POSI', max_length=2)  # Field name made lowercase.
    chin = models.IntegerField(db_column='CHIN')  # Field name made lowercase.
    chturn = models.CharField(db_column='CHTURN', max_length=10)  # Field name made lowercase.
    chbcnt = models.IntegerField(db_column='CHBCNT')  # Field name made lowercase.
    chin2 = models.CharField(db_column='CHIN2', max_length=10)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'entry'
        unique_together = (('gyear', 'turn', 'pcode', 'posi', 'gmkey'),)


class Entrydaily(models.Model):
    gamedate = models.CharField(max_length=8)
    tcode = models.CharField(max_length=20)
    pcode = models.CharField(max_length=10)
    reg = models.CharField(max_length=1, blank=True, null=True)
    inputtime = models.DateTimeField()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'entrydaily'


class Gamecontapp(models.Model):
    gmkey = models.CharField(db_column='GMKEY', primary_key=True, max_length=13)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    gday = models.CharField(db_column='GDAY', max_length=8)  # Field name made lowercase.
    serno = models.SmallIntegerField(db_column='SERNO')  # Field name made lowercase.
    turn = models.CharField(db_column='TURN', max_length=2)  # Field name made lowercase.
    inn = models.IntegerField(db_column='INN')  # Field name made lowercase.
    tb = models.CharField(db_column='TB', max_length=1)  # Field name made lowercase.
    inn2 = models.CharField(db_column='INN2', max_length=1, blank=True, null=True)  # Field name made lowercase.
    ocount = models.CharField(db_column='OCOUNT', max_length=1, blank=True, null=True)  # Field name made lowercase.
    bcount = models.CharField(db_column='BCOUNT', max_length=30, blank=True, null=True)  # Field name made lowercase.
    rturn = models.CharField(db_column='RTURN', max_length=2, blank=True, null=True)  # Field name made lowercase.
    how = models.CharField(db_column='HOW', max_length=2, blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='FIELD', max_length=25, blank=True, null=True)  # Field name made lowercase.
    place = models.CharField(db_column='PLACE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    hitter = models.CharField(db_column='HITTER', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hitname = models.CharField(db_column='HITNAME', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pitname = models.CharField(db_column='PITNAME', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pitcher = models.CharField(db_column='PITCHER', max_length=10, blank=True, null=True)  # Field name made lowercase.
    catname = models.CharField(db_column='CATNAME', max_length=20, blank=True, null=True)  # Field name made lowercase.
    catcher = models.CharField(db_column='CATCHER', max_length=10, blank=True, null=True)  # Field name made lowercase.
    bcnt = models.CharField(db_column='BCNT', max_length=3, blank=True, null=True)  # Field name made lowercase.
    tscore = models.SmallIntegerField(db_column='TSCORE', blank=True, null=True)  # Field name made lowercase.
    bscore = models.SmallIntegerField(db_column='BSCORE', blank=True, null=True)  # Field name made lowercase.
    base1b = models.CharField(db_column='BASE1B', max_length=2, blank=True, null=True)  # Field name made lowercase.
    base2b = models.CharField(db_column='BASE2B', max_length=2, blank=True, null=True)  # Field name made lowercase.
    base3b = models.CharField(db_column='BASE3B', max_length=2, blank=True, null=True)  # Field name made lowercase.
    base1a = models.CharField(db_column='BASE1A', max_length=2, blank=True, null=True)  # Field name made lowercase.
    base2a = models.CharField(db_column='BASE2A', max_length=2, blank=True, null=True)  # Field name made lowercase.
    base3a = models.CharField(db_column='BASE3A', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'gamecontapp'
        unique_together = (('gmkey', 'serno'),)


class Gameinfo(models.Model):
    gmkey = models.CharField(db_column='GmKey', primary_key=True, max_length=13)  # Field name made lowercase.
    gday = models.CharField(db_column='Gday', max_length=8)  # Field name made lowercase.
    dbhd = models.CharField(db_column='Dbhd', max_length=10)  # Field name made lowercase.
    stadium = models.CharField(db_column='Stadium', max_length=20)  # Field name made lowercase.
    vteam = models.CharField(db_column='Vteam', max_length=2)  # Field name made lowercase.
    hteam = models.CharField(db_column='Hteam', max_length=2)  # Field name made lowercase.
    sttm = models.CharField(db_column='Sttm', max_length=4)  # Field name made lowercase.
    entm = models.CharField(db_column='Entm', max_length=4)  # Field name made lowercase.
    dltm = models.CharField(db_column='Dltm', max_length=4)  # Field name made lowercase.
    gmtm = models.CharField(db_column='Gmtm', max_length=4)  # Field name made lowercase.
    stad = models.CharField(db_column='Stad', max_length=8)  # Field name made lowercase.
    umpc = models.CharField(db_column='Umpc', max_length=8)  # Field name made lowercase.
    ump1 = models.CharField(db_column='Ump1', max_length=8)  # Field name made lowercase.
    ump2 = models.CharField(db_column='Ump2', max_length=8)  # Field name made lowercase.
    ump3 = models.CharField(db_column='Ump3', max_length=8)  # Field name made lowercase.
    umpl = models.CharField(db_column='Umpl', max_length=8, blank=True, null=True)  # Field name made lowercase.
    umpr = models.CharField(db_column='Umpr', max_length=8, blank=True, null=True)  # Field name made lowercase.
    scoa = models.CharField(db_column='Scoa', max_length=8)  # Field name made lowercase.
    scob = models.CharField(db_column='Scob', max_length=8)  # Field name made lowercase.
    temp = models.CharField(db_column='Temp', max_length=3)  # Field name made lowercase.
    mois = models.CharField(db_column='Mois', max_length=3)  # Field name made lowercase.
    weath = models.CharField(db_column='Weath', max_length=4)  # Field name made lowercase.
    wind = models.CharField(db_column='Wind', max_length=3)  # Field name made lowercase.
    wins = models.CharField(db_column='Wins', max_length=5)  # Field name made lowercase.
    gweek = models.CharField(db_column='Gweek', max_length=2, blank=True, null=True)  # Field name made lowercase.
    crowd = models.IntegerField(db_column='Crowd')  # Field name made lowercase.
    chajun = models.CharField(db_column='Chajun', max_length=2)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'gameinfo'


class Hitter(models.Model):
    gmkey = models.CharField(db_column='GMKEY', primary_key=True, max_length=13)  # Field name made lowercase.
    gday = models.CharField(db_column='GDAY', max_length=8)  # Field name made lowercase.
    tb = models.CharField(db_column='TB', max_length=1, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=30, blank=True, null=True)  # Field name made lowercase.
    pcode = models.CharField(db_column='PCODE', max_length=5)  # Field name made lowercase.
    turn = models.CharField(db_column='TURN', max_length=2, blank=True, null=True)  # Field name made lowercase.
    oneturn = models.CharField(db_column='ONETURN', max_length=1, blank=True, null=True)  # Field name made lowercase.
    pa = models.IntegerField(db_column='PA', blank=True, null=True)  # Field name made lowercase.
    ab = models.IntegerField(db_column='AB', blank=True, null=True)  # Field name made lowercase.
    rbi = models.IntegerField(db_column='RBI', blank=True, null=True)  # Field name made lowercase.
    run = models.IntegerField(db_column='RUN', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    h2 = models.IntegerField(db_column='H2', blank=True, null=True)  # Field name made lowercase.
    h3 = models.IntegerField(db_column='H3', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    sb = models.IntegerField(db_column='SB', blank=True, null=True)  # Field name made lowercase.
    cs = models.IntegerField(db_column='CS', blank=True, null=True)  # Field name made lowercase.
    sh = models.IntegerField(db_column='SH', blank=True, null=True)  # Field name made lowercase.
    sf = models.IntegerField(db_column='SF', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    ib = models.IntegerField(db_column='IB', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.
    kk = models.IntegerField(db_column='KK', blank=True, null=True)  # Field name made lowercase.
    gd = models.IntegerField(db_column='GD', blank=True, null=True)  # Field name made lowercase.
    err = models.IntegerField(db_column='ERR', blank=True, null=True)  # Field name made lowercase.
    lob = models.IntegerField(db_column='LOB', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(db_column='SCORE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'hitter'
        unique_together = (('gmkey', 'pcode', 'gday'),)


class IeGamelist(models.Model):
    gameid = models.CharField(db_column='gameID', primary_key=True, max_length=20)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    homename = models.CharField(db_column='HomeName', max_length=20, blank=True, null=True)  # Field name made lowercase.
    homemascot = models.CharField(db_column='HomeMascot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    visitname = models.CharField(db_column='VisitName', max_length=20, blank=True, null=True)  # Field name made lowercase.
    visitmascot = models.CharField(db_column='VisitMascot', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'ie_gamelist'
        unique_together = (('gameid', 'gyear'),)


class IeInningrecord(models.Model):
    gameid = models.CharField(db_column='GAMEID', primary_key=True, max_length=13)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    inning = models.IntegerField(db_column='INNING')  # Field name made lowercase.
    tb = models.CharField(db_column='TB', max_length=1)  # Field name made lowercase.
    run = models.IntegerField(db_column='RUN', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    err = models.IntegerField(db_column='ERR', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    lob = models.IntegerField(db_column='LOB', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'ie_inningrecord'
        unique_together = (('gameid', 'gyear', 'inning', 'tb'),)


class IeLivetextScoreMix(models.Model):
    gameid = models.CharField(db_column='gameID', primary_key=True, max_length=13)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    seqno = models.IntegerField(db_column='seqNO')  # Field name made lowercase.
    inning = models.IntegerField(blank=True, null=True)
    ilsun = models.IntegerField(blank=True, null=True)
    btop = models.IntegerField(db_column='bTop', blank=True, null=True)  # Field name made lowercase.
    ballcount = models.IntegerField(blank=True, null=True)
    ball_type = models.CharField(max_length=10, blank=True, null=True)
    strike = models.IntegerField(blank=True, null=True)
    ball = models.IntegerField(blank=True, null=True)
    out = models.IntegerField(blank=True, null=True)
    pitcher = models.CharField(max_length=10, blank=True, null=True)
    batter = models.CharField(max_length=10, blank=True, null=True)
    catcher = models.CharField(max_length=10, blank=True, null=True)
    runner = models.CharField(max_length=10, blank=True, null=True)
    batorder = models.IntegerField(blank=True, null=True)
    batstartorder = models.IntegerField(blank=True, null=True)
    batresult = models.CharField(db_column='batResult', max_length=50, blank=True, null=True)  # Field name made lowercase.
    base1 = models.IntegerField(blank=True, null=True)
    base2 = models.IntegerField(blank=True, null=True)
    base3 = models.IntegerField(blank=True, null=True)
    a_score = models.IntegerField(db_column='A_Score', blank=True, null=True)  # Field name made lowercase.
    h_score = models.IntegerField(db_column='H_Score', blank=True, null=True)  # Field name made lowercase.
    a_run = models.IntegerField(db_column='A_Run', blank=True, null=True)  # Field name made lowercase.
    h_run = models.IntegerField(db_column='H_Run', blank=True, null=True)  # Field name made lowercase.
    a_hit = models.IntegerField(db_column='A_Hit', blank=True, null=True)  # Field name made lowercase.
    h_hit = models.IntegerField(db_column='H_Hit', blank=True, null=True)  # Field name made lowercase.
    a_error = models.IntegerField(db_column='A_Error', blank=True, null=True)  # Field name made lowercase.
    h_error = models.IntegerField(db_column='H_Error', blank=True, null=True)  # Field name made lowercase.
    a_ballfour = models.IntegerField(db_column='A_BallFour', blank=True, null=True)  # Field name made lowercase.
    h_ballfour = models.IntegerField(db_column='H_BallFour', blank=True, null=True)  # Field name made lowercase.
    livetext = models.CharField(db_column='LiveText', max_length=200, blank=True, null=True)  # Field name made lowercase.
    textstyle = models.IntegerField(db_column='textStyle', blank=True, null=True)  # Field name made lowercase.
    state_sc = models.IntegerField(db_column='STATE_SC', blank=True, null=True)  # Field name made lowercase.
    how = models.CharField(db_column='HOW', max_length=2, blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'ie_livetext_score_mix'
        unique_together = (('gameid', 'gyear', 'seqno'),)


class IeRecordMatrixMix(models.Model):
    gameid = models.CharField(db_column='GAMEID', primary_key=True, max_length=13)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    seqno = models.SmallIntegerField(db_column='SEQNO')  # Field name made lowercase.
    inn_no = models.IntegerField(db_column='INN_NO')  # Field name made lowercase.
    bat_around_no = models.IntegerField(db_column='BAT_AROUND_NO')  # Field name made lowercase.
    tb_sc = models.CharField(db_column='TB_SC', max_length=1)  # Field name made lowercase.
    before_out_cn = models.SmallIntegerField(db_column='BEFORE_OUT_CN')  # Field name made lowercase.
    before_away_score_cn = models.SmallIntegerField(db_column='BEFORE_AWAY_SCORE_CN')  # Field name made lowercase.
    before_home_score_cn = models.SmallIntegerField(db_column='BEFORE_HOME_SCORE_CN')  # Field name made lowercase.
    before_score_gap_cn = models.SmallIntegerField(db_column='BEFORE_SCORE_GAP_CN')  # Field name made lowercase.
    before_runner_sc = models.SmallIntegerField(db_column='BEFORE_RUNNER_SC')  # Field name made lowercase.
    after_out_cn = models.SmallIntegerField(db_column='AFTER_OUT_CN')  # Field name made lowercase.
    after_away_score_cn = models.SmallIntegerField(db_column='AFTER_AWAY_SCORE_CN')  # Field name made lowercase.
    after_home_score_cn = models.SmallIntegerField(db_column='AFTER_HOME_SCORE_CN')  # Field name made lowercase.
    after_score_gap_cn = models.SmallIntegerField(db_column='AFTER_SCORE_GAP_CN')  # Field name made lowercase.
    after_runner_sc = models.SmallIntegerField(db_column='AFTER_RUNNER_SC')  # Field name made lowercase.
    bat_p_id = models.IntegerField(db_column='BAT_P_ID', blank=True, null=True)  # Field name made lowercase.
    pit_p_id = models.IntegerField(db_column='PIT_P_ID', blank=True, null=True)  # Field name made lowercase.
    run_p_id = models.IntegerField(db_column='RUN_P_ID', blank=True, null=True)  # Field name made lowercase.
    how_id = models.CharField(db_column='HOW_ID', max_length=2, blank=True, null=True)  # Field name made lowercase.
    livetext_if = models.CharField(db_column='LIVETEXT_IF', max_length=400, blank=True, null=True)  # Field name made lowercase.
    before_we_rt = models.FloatField(db_column='BEFORE_WE_RT', blank=True, null=True)  # Field name made lowercase.
    after_we_rt = models.FloatField(db_column='AFTER_WE_RT', blank=True, null=True)  # Field name made lowercase.
    wpa_rt = models.FloatField(db_column='WPA_RT', blank=True, null=True)  # Field name made lowercase.
    li_rt = models.FloatField(db_column='LI_RT', blank=True, null=True)  # Field name made lowercase.
    re_rt = models.FloatField(db_column='RE_RT', blank=True, null=True)  # Field name made lowercase.
    reg_dt = models.DateField(db_column='REG_DT', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'ie_record_matrix_mix'
        unique_together = (('gameid', 'gyear', 'seqno'),)


class IeScoreinning(models.Model):
    gameid = models.CharField(db_column='gameID', primary_key=True, max_length=20)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    inning = models.IntegerField()
    score = models.IntegerField(db_column='Score')  # Field name made lowercase.
    bhome = models.IntegerField(db_column='bHome')  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'ie_scoreinning'
        unique_together = (('gameid', 'gyear', 'inning', 'bhome'),)


class MajorNamed(models.Model):
    pcode = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=20)
    game_count = models.IntegerField()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'major_named'
        unique_together = (('pcode', 'name'),)


class MatrixBasic(models.Model):
    season_id = models.SmallIntegerField(db_column='SEASON_ID')  # Field name made lowercase.
    out_cn = models.IntegerField(db_column='OUT_CN')  # Field name made lowercase.
    runner_sc = models.IntegerField(db_column='RUNNER_SC')  # Field name made lowercase.
    re_rt = models.FloatField(db_column='RE_RT', blank=True, null=True)  # Field name made lowercase.
    reg_dt = models.DateTimeField(db_column='REG_DT', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'matrix_basic'


class MatrixDetail(models.Model):
    season_id = models.SmallIntegerField(db_column='SEASON_ID', primary_key=True)  # Field name made lowercase.
    inn_no = models.IntegerField(db_column='INN_NO')  # Field name made lowercase.
    tb_sc = models.CharField(db_column='TB_SC', max_length=1)  # Field name made lowercase.
    out_cn = models.IntegerField(db_column='OUT_CN')  # Field name made lowercase.
    runner_sc = models.IntegerField(db_column='RUNNER_SC')  # Field name made lowercase.
    score_gap_cn = models.SmallIntegerField(db_column='SCORE_GAP_CN')  # Field name made lowercase.
    we_rt = models.FloatField(db_column='WE_RT', blank=True, null=True)  # Field name made lowercase.
    li_rt = models.FloatField(db_column='LI_RT')  # Field name made lowercase.
    reg_dt = models.DateTimeField(db_column='REG_DT', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'matrix_detail'
        unique_together = (('season_id', 'inn_no', 'tb_sc', 'out_cn', 'runner_sc', 'score_gap_cn'),)


class Person(models.Model):
    name = models.CharField(db_column='NAME', max_length=20)  # Field name made lowercase.
    pcode = models.CharField(db_column='PCODE', primary_key=True, max_length=5)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=255, blank=True, null=True)  # Field name made lowercase.
    position = models.CharField(db_column='POSITION', max_length=255, blank=True, null=True)  # Field name made lowercase.
    pos = models.CharField(db_column='POS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    backnum = models.CharField(db_column='BACKNUM', max_length=6, blank=True, null=True)  # Field name made lowercase.
    cname = models.CharField(db_column='CNAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    birth = models.CharField(db_column='BIRTH', max_length=255, blank=True, null=True)  # Field name made lowercase.
    height = models.CharField(db_column='HEIGHT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    weight = models.CharField(db_column='WEIGHT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    career = models.CharField(db_column='CAREER', max_length=255, blank=True, null=True)  # Field name made lowercase.
    hittype = models.CharField(db_column='HITTYPE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    indate = models.CharField(db_column='INDATE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    promise = models.CharField(db_column='PROMISE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    money = models.CharField(db_column='MONEY', max_length=255, blank=True, null=True)  # Field name made lowercase.
    addr = models.CharField(db_column='ADDR', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nickname = models.CharField(db_column='NICKNAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    hobby = models.CharField(db_column='HOBBY', max_length=255, blank=True, null=True)  # Field name made lowercase.
    entry = models.CharField(db_column='ENTRY', max_length=1, blank=True, null=True)  # Field name made lowercase.
    img1 = models.CharField(db_column='IMG1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    img2 = models.CharField(db_column='IMG2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    career2 = models.CharField(db_column='CAREER2', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'person'


class PersonInfo(models.Model):
    pcode = models.CharField(db_column='PCODE', primary_key=True, max_length=10)  # Field name made lowercase.
    p_kor_full_nm = models.CharField(db_column='P_KOR_FULL_NM', max_length=60, blank=True, null=True)  # Field name made lowercase.
    draft_if = models.CharField(db_column='DRAFT_IF', max_length=50, blank=True, null=True)  # Field name made lowercase.
    career_if = models.CharField(db_column='CAREER_IF', max_length=200, blank=True, null=True)  # Field name made lowercase.
    international_if = models.CharField(db_column='INTERNATIONAL_IF', max_length=200, blank=True, null=True)  # Field name made lowercase.
    reg_dt = models.DateTimeField(db_column='REG_DT')  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'person_info'


class Pitcher(models.Model):
    gmkey = models.CharField(db_column='GMKEY', primary_key=True, max_length=13)  # Field name made lowercase.
    gday = models.CharField(db_column='GDAY', max_length=8)  # Field name made lowercase.
    tb = models.CharField(db_column='TB', max_length=1, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pcode = models.CharField(db_column='PCODE', max_length=5)  # Field name made lowercase.
    pos = models.CharField(db_column='POS', max_length=10, blank=True, null=True)  # Field name made lowercase.
    start = models.CharField(db_column='START', max_length=3, blank=True, null=True)  # Field name made lowercase.
    quit = models.CharField(db_column='QUIT', max_length=3, blank=True, null=True)  # Field name made lowercase.
    cg = models.IntegerField(db_column='CG', blank=True, null=True)  # Field name made lowercase.
    sho = models.IntegerField(db_column='SHO', blank=True, null=True)  # Field name made lowercase.
    wls = models.CharField(db_column='WLS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    hold = models.SmallIntegerField(db_column='HOLD', blank=True, null=True)  # Field name made lowercase.
    inn = models.CharField(db_column='INN', max_length=10, blank=True, null=True)  # Field name made lowercase.
    inn2 = models.IntegerField(db_column='INN2', blank=True, null=True)  # Field name made lowercase.
    bf = models.IntegerField(db_column='BF', blank=True, null=True)  # Field name made lowercase.
    pa = models.IntegerField(db_column='PA', blank=True, null=True)  # Field name made lowercase.
    ab = models.IntegerField(db_column='AB', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    h2 = models.IntegerField(db_column='H2', blank=True, null=True)  # Field name made lowercase.
    h3 = models.IntegerField(db_column='H3', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    sb = models.IntegerField(db_column='SB', blank=True, null=True)  # Field name made lowercase.
    cs = models.IntegerField(db_column='CS', blank=True, null=True)  # Field name made lowercase.
    sh = models.IntegerField(db_column='SH', blank=True, null=True)  # Field name made lowercase.
    sf = models.IntegerField(db_column='SF', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    ib = models.IntegerField(db_column='IB', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.
    kk = models.IntegerField(db_column='KK', blank=True, null=True)  # Field name made lowercase.
    gd = models.IntegerField(db_column='GD', blank=True, null=True)  # Field name made lowercase.
    wp = models.IntegerField(db_column='WP', blank=True, null=True)  # Field name made lowercase.
    bk = models.IntegerField(db_column='BK', blank=True, null=True)  # Field name made lowercase.
    err = models.IntegerField(db_column='ERR', blank=True, null=True)  # Field name made lowercase.
    r = models.IntegerField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    er = models.IntegerField(db_column='ER', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(db_column='SCORE', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'pitcher'
        unique_together = (('gmkey', 'pcode', 'gday'),)


class Pittotal(models.Model):
    pcode = models.CharField(db_column='PCODE', primary_key=True, max_length=5)  # Field name made lowercase.
    gyear = models.CharField(db_column='GYEAR', max_length=4)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=10, blank=True, null=True)  # Field name made lowercase.
    era = models.FloatField(db_column='ERA', blank=True, null=True)  # Field name made lowercase.
    gamenum = models.IntegerField(db_column='GAMENUM', blank=True, null=True)  # Field name made lowercase.
    cg = models.IntegerField(db_column='CG', blank=True, null=True)  # Field name made lowercase.
    sho = models.IntegerField(db_column='SHO', blank=True, null=True)  # Field name made lowercase.
    w = models.IntegerField(db_column='W', blank=True, null=True)  # Field name made lowercase.
    l = models.IntegerField(db_column='L', blank=True, null=True)  # Field name made lowercase.
    sv = models.IntegerField(db_column='SV', blank=True, null=True)  # Field name made lowercase.
    hold = models.PositiveIntegerField(db_column='HOLD', blank=True, null=True)  # Field name made lowercase.
    bf = models.IntegerField(db_column='BF', blank=True, null=True)  # Field name made lowercase.
    inn = models.CharField(db_column='INN', max_length=15, blank=True, null=True)  # Field name made lowercase.
    inn2 = models.IntegerField(db_column='INN2', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.
    kk = models.IntegerField(db_column='KK', blank=True, null=True)  # Field name made lowercase.
    r = models.IntegerField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    er = models.IntegerField(db_column='ER', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(db_column='SCORE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'pittotal'
        unique_together = (('pcode', 'gyear'),)


class RareRecords(models.Model):
    gmkey = models.CharField(max_length=13)
    gday = models.CharField(max_length=8)
    name = models.CharField(max_length=10)
    pcode = models.CharField(max_length=5)
    player_team = models.CharField(max_length=2)
    versus_team = models.CharField(max_length=2)
    record_name = models.CharField(primary_key=True, max_length=20)
    record_order = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'real_minor_baseball'
        managed = False
        db_table = 'rare_records'
        unique_together = (('record_name', 'gmkey', 'pcode'),)


class RecordMatrixMix(models.Model):
    gameid = models.CharField(db_column='GAMEID', primary_key=True, max_length=13)  # Field name made lowercase.
    gyear = models.SmallIntegerField(db_column='GYEAR')  # Field name made lowercase.
    seqno = models.SmallIntegerField(db_column='SEQNO')  # Field name made lowercase.
    inn_no = models.IntegerField(db_column='INN_NO')  # Field name made lowercase.
    bat_around_no = models.IntegerField(db_column='BAT_AROUND_NO')  # Field name made lowercase.
    tb_sc = models.CharField(db_column='TB_SC', max_length=1)  # Field name made lowercase.
    before_out_cn = models.SmallIntegerField(db_column='BEFORE_OUT_CN')  # Field name made lowercase.
    before_away_score_cn = models.SmallIntegerField(db_column='BEFORE_AWAY_SCORE_CN')  # Field name made lowercase.
    before_home_score_cn = models.SmallIntegerField(db_column='BEFORE_HOME_SCORE_CN')  # Field name made lowercase.
    before_score_gap_cn = models.SmallIntegerField(db_column='BEFORE_SCORE_GAP_CN')  # Field name made lowercase.
    before_runner_sc = models.SmallIntegerField(db_column='BEFORE_RUNNER_SC')  # Field name made lowercase.
    after_out_cn = models.SmallIntegerField(db_column='AFTER_OUT_CN')  # Field name made lowercase.
    after_away_score_cn = models.SmallIntegerField(db_column='AFTER_AWAY_SCORE_CN')  # Field name made lowercase.
    after_home_score_cn = models.SmallIntegerField(db_column='AFTER_HOME_SCORE_CN')  # Field name made lowercase.
    after_score_gap_cn = models.SmallIntegerField(db_column='AFTER_SCORE_GAP_CN')  # Field name made lowercase.
    after_runner_sc = models.SmallIntegerField(db_column='AFTER_RUNNER_SC')  # Field name made lowercase.
    bat_p_id = models.IntegerField(db_column='BAT_P_ID', blank=True, null=True)  # Field name made lowercase.
    pit_p_id = models.IntegerField(db_column='PIT_P_ID', blank=True, null=True)  # Field name made lowercase.
    run_p_id = models.IntegerField(db_column='RUN_P_ID', blank=True, null=True)  # Field name made lowercase.
    how_id = models.CharField(db_column='HOW_ID', max_length=4, blank=True, null=True)  # Field name made lowercase.
    livetext_if = models.CharField(db_column='LIVETEXT_IF', max_length=400, blank=True, null=True)  # Field name made lowercase.
    before_we_rt = models.FloatField(db_column='BEFORE_WE_RT', blank=True, null=True)  # Field name made lowercase.
    after_we_rt = models.FloatField(db_column='AFTER_WE_RT', blank=True, null=True)  # Field name made lowercase.
    wpa_rt = models.FloatField(db_column='WPA_RT', blank=True, null=True)  # Field name made lowercase.
    li_rt = models.FloatField(db_column='LI_RT', blank=True, null=True)  # Field name made lowercase.
    re_rt = models.FloatField(db_column='RE_RT', blank=True, null=True)  # Field name made lowercase.
    reg_dt = models.DateField(db_column='REG_DT', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'record_matrix_mix'
        unique_together = (('gameid', 'gyear', 'seqno'),)


class RobotArticle(models.Model):
    game_id = models.CharField(primary_key=True, max_length=13)
    le_id = models.IntegerField()
    serial = models.IntegerField()
    gyear = models.CharField(max_length=4)
    status = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    article = models.CharField(max_length=5000, blank=True, null=True)
    created_at = models.DateTimeField()
    time_key = models.CharField(max_length=15)

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'robot_article'
        unique_together = (('game_id', 'serial', 'gyear', 'time_key'),)


class RobotArticleHistory(models.Model):
    game_id = models.CharField(primary_key=True, max_length=13)
    le_id = models.IntegerField()
    serial = models.IntegerField()
    gyear = models.CharField(max_length=4)
    status = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    article = models.CharField(max_length=5000, blank=True, null=True)
    created_at = models.DateTimeField()
    time_key = models.CharField(max_length=15)

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'robot_article_history'
        unique_together = (('game_id', 'serial', 'gyear', 'time_key'),)


class Score(models.Model):
    gmkey = models.CharField(db_column='GMKEY', primary_key=True, max_length=13)  # Field name made lowercase.
    gday = models.CharField(db_column='GDAY', max_length=8)  # Field name made lowercase.
    number_1t = models.IntegerField(db_column='1T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_1b = models.IntegerField(db_column='1B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_2t = models.IntegerField(db_column='2T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_2b = models.IntegerField(db_column='2B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_3t = models.IntegerField(db_column='3T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_3b = models.IntegerField(db_column='3B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_4t = models.IntegerField(db_column='4T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_4b = models.IntegerField(db_column='4B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_5t = models.IntegerField(db_column='5T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_5b = models.IntegerField(db_column='5B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_6t = models.IntegerField(db_column='6T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_6b = models.IntegerField(db_column='6B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_7t = models.IntegerField(db_column='7T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_7b = models.IntegerField(db_column='7B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_8t = models.IntegerField(db_column='8T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_8b = models.IntegerField(db_column='8B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_9t = models.IntegerField(db_column='9T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_9b = models.IntegerField(db_column='9B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_10t = models.IntegerField(db_column='10T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_10b = models.IntegerField(db_column='10B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_11t = models.IntegerField(db_column='11T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_11b = models.IntegerField(db_column='11B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_12t = models.IntegerField(db_column='12T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_12b = models.IntegerField(db_column='12B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_13t = models.IntegerField(db_column='13T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_13b = models.IntegerField(db_column='13B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_14t = models.IntegerField(db_column='14T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_14b = models.IntegerField(db_column='14B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_15t = models.IntegerField(db_column='15T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_15b = models.IntegerField(db_column='15B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_16t = models.IntegerField(db_column='16T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_16b = models.IntegerField(db_column='16B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_17t = models.IntegerField(db_column='17T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_17b = models.IntegerField(db_column='17B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_18t = models.IntegerField(db_column='18T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_18b = models.IntegerField(db_column='18B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_19t = models.IntegerField(db_column='19T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_19b = models.IntegerField(db_column='19B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_20t = models.IntegerField(db_column='20T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_20b = models.IntegerField(db_column='20B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_21t = models.IntegerField(db_column='21T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_21b = models.IntegerField(db_column='21B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_22t = models.IntegerField(db_column='22T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_22b = models.IntegerField(db_column='22B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_23t = models.IntegerField(db_column='23T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_23b = models.IntegerField(db_column='23B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_24t = models.IntegerField(db_column='24T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_24b = models.IntegerField(db_column='24B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_25t = models.IntegerField(db_column='25T', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    number_25b = models.IntegerField(db_column='25B', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    tpoint = models.IntegerField(db_column='TPOINT', blank=True, null=True)  # Field name made lowercase.
    bpoint = models.IntegerField(db_column='BPOINT', blank=True, null=True)  # Field name made lowercase.
    thit = models.IntegerField(db_column='THIT', blank=True, null=True)  # Field name made lowercase.
    bhit = models.IntegerField(db_column='BHIT', blank=True, null=True)  # Field name made lowercase.
    terr = models.IntegerField(db_column='TERR', blank=True, null=True)  # Field name made lowercase.
    berr = models.IntegerField(db_column='BERR', blank=True, null=True)  # Field name made lowercase.
    tbbhp = models.IntegerField(db_column='TBBHP', blank=True, null=True)  # Field name made lowercase.
    bbbhp = models.IntegerField(db_column='BBBHP', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'score'
        unique_together = (('gmkey', 'gday'),)


class TeamLeague(models.Model):
    gyear = models.CharField(primary_key=True, max_length=4)
    team = models.CharField(max_length=2)
    teamname = models.CharField(max_length=10)
    league = models.CharField(max_length=10)

    objects = models.Manager()

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'team_league'
        unique_together = (('gyear', 'team'),)


class Teamrank(models.Model):
    gyear = models.CharField(db_column='GYEAR', primary_key=True, max_length=4)  # Field name made lowercase.
    rank = models.IntegerField(db_column='RANK')  # Field name made lowercase.
    league = models.CharField(db_column='LEAGUE', max_length=5, blank=True, null=True)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=12)  # Field name made lowercase.
    game = models.IntegerField(db_column='GAME', blank=True, null=True)  # Field name made lowercase.
    win = models.IntegerField(db_column='WIN', blank=True, null=True)  # Field name made lowercase.
    lose = models.IntegerField(db_column='LOSE', blank=True, null=True)  # Field name made lowercase.
    same = models.IntegerField(db_column='SAME', blank=True, null=True)  # Field name made lowercase.
    wra = models.FloatField(db_column='WRA', blank=True, null=True)  # Field name made lowercase.
    ab = models.IntegerField(db_column='AB', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    sb = models.IntegerField(db_column='SB', blank=True, null=True)  # Field name made lowercase.
    run = models.IntegerField(db_column='RUN', blank=True, null=True)  # Field name made lowercase.
    inn = models.CharField(db_column='INN', max_length=10, blank=True, null=True)  # Field name made lowercase.
    inn2 = models.IntegerField(db_column='INN2', blank=True, null=True)  # Field name made lowercase.
    r = models.IntegerField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    er = models.IntegerField(db_column='ER', blank=True, null=True)  # Field name made lowercase.
    err = models.IntegerField(db_column='ERR', blank=True, null=True)  # Field name made lowercase.
    hra = models.CharField(db_column='HRA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lra = models.CharField(db_column='LRA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bra = models.CharField(db_column='BRA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    era = models.CharField(db_column='ERA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dra = models.CharField(db_column='DRA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    continue_field = models.CharField(db_column='CONTINUE', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    h2 = models.IntegerField(db_column='H2', blank=True, null=True)  # Field name made lowercase.
    h3 = models.IntegerField(db_column='H3', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.
    sf = models.IntegerField(db_column='SF', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'teamrank'
        unique_together = (('gyear', 'team', 'rank'),)


class TeamrankDaily(models.Model):
    gyear = models.CharField(db_column='GYEAR', primary_key=True, max_length=13)  # Field name made lowercase.
    rank = models.IntegerField(db_column='RANK', blank=True, null=True)  # Field name made lowercase.
    league = models.CharField(db_column='LEAGUE', max_length=13, blank=True, null=True)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=13)  # Field name made lowercase.
    game = models.IntegerField(db_column='GAME', blank=True, null=True)  # Field name made lowercase.
    win = models.IntegerField(db_column='WIN', blank=True, null=True)  # Field name made lowercase.
    lose = models.IntegerField(db_column='LOSE', blank=True, null=True)  # Field name made lowercase.
    same = models.IntegerField(db_column='SAME', blank=True, null=True)  # Field name made lowercase.
    wra = models.FloatField(db_column='WRA', blank=True, null=True)  # Field name made lowercase.
    ab = models.IntegerField(db_column='AB', blank=True, null=True)  # Field name made lowercase.
    hit = models.IntegerField(db_column='HIT', blank=True, null=True)  # Field name made lowercase.
    hr = models.IntegerField(db_column='HR', blank=True, null=True)  # Field name made lowercase.
    sb = models.IntegerField(db_column='SB', blank=True, null=True)  # Field name made lowercase.
    run = models.IntegerField(db_column='RUN', blank=True, null=True)  # Field name made lowercase.
    inn = models.CharField(db_column='INN', max_length=10, blank=True, null=True)  # Field name made lowercase.
    inn2 = models.IntegerField(db_column='INN2', blank=True, null=True)  # Field name made lowercase.
    r = models.IntegerField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    er = models.IntegerField(db_column='ER', blank=True, null=True)  # Field name made lowercase.
    err = models.IntegerField(db_column='ERR', blank=True, null=True)  # Field name made lowercase.
    hra = models.CharField(db_column='HRA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    lra = models.CharField(db_column='LRA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    bra = models.CharField(db_column='BRA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    era = models.CharField(db_column='ERA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    dra = models.CharField(db_column='DRA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    continue_field = models.CharField(db_column='CONTINUE', max_length=10, blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    h2 = models.IntegerField(db_column='H2', blank=True, null=True)  # Field name made lowercase.
    h3 = models.IntegerField(db_column='H3', blank=True, null=True)  # Field name made lowercase.
    bb = models.IntegerField(db_column='BB', blank=True, null=True)  # Field name made lowercase.
    hp = models.IntegerField(db_column='HP', blank=True, null=True)  # Field name made lowercase.
    sf = models.IntegerField(db_column='SF', blank=True, null=True)  # Field name made lowercase.
    date = models.CharField(max_length=10)

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'teamrank_daily'
        unique_together = (('gyear', 'team', 'date'),)


class KboEtcgame(models.Model):
    gyear = models.CharField(db_column='GYEAR', primary_key=True, max_length=4)
    gmkey = models.CharField(db_column='GMKEY', max_length=13)  # Field name made lowercase.
    gday = models.CharField(db_column='GDAY', max_length=8)  # Field name made lowercase.
    seq = models.IntegerField(db_column='SEQ', max_length=10)  # Field name made lowercase.
    how = models.CharField(db_column='HOW', max_length=100, blank=True, null=True)  # Field name made lowercase.
    result = models.CharField(db_column='RESULT', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'kbo_etcgame'
        unique_together = (('gmkey', 'gyear'),)


class EtcGame(models.Model):
    gyear = models.CharField(db_column='GYEAR', primary_key=True, max_length=4)
    gmkey = models.CharField(db_column='GMKEY', max_length=13)  # Field name made lowercase.
    ser = models.IntegerField(db_column='SER', max_length=10)  # Field name made lowercase.
    how = models.CharField(db_column='HOW', max_length=4, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=10, blank=True, null=True)  # Field name made lowercase.
    pcode = models.CharField(db_column='PCODE', max_length=5, blank=True, null=True)  # Field name made lowercase.
    inn = models.IntegerField(db_column='INN', blank=True, null=True)  # Field name made lowercase.
    name2 = models.CharField(db_column='NAME2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    pcode2 = models.CharField(db_column='PCODE2', max_length=5, blank=True, null=True)  # Field name made lowercase.
    etc1 = models.CharField(db_column='ETC1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    etc2 = models.CharField(db_column='ETC2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        app_label = 'minor_baseball'
        managed = False
        db_table = 'etcgame'
        unique_together = (('gmkey', 'gyear', 'ser'),)

