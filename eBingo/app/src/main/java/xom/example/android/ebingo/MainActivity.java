package xom.example.android.ebingo;

import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Vibrator;
import android.speech.tts.TextToSpeech;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Half;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.Locale;
import java.util.Random;

public class MainActivity extends AppCompatActivity {

    TextToSpeech messagespeech;
    EditText    ed1;
    Button b1;
    String request;
    String message;

    //IP address of the MQTT broker
    static String MQTTHOST="tcp://192.168.0.10";
    //username and password of device connectd to MQTT broker
    static String USERNAME="loizospap";
    static String PASSWORD="123456";
    //topic to publish
    static String topic_stream_publish="esys/cringo/samples/subscribe";
    //topic to subscribe
    static String topic_stream_subscribe="esys/cringo/samples/publish";


    MqttAndroidClient client;

    TextView subText;

    MqttConnectOptions options;

    Vibrator vibrator;

    Ringtone myRingtone;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        subText=(TextView)findViewById(R.id.subText);

        vibrator=(Vibrator)getSystemService(VIBRATOR_SERVICE);

        Uri uri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        myRingtone=RingtoneManager.getRingtone(getApplicationContext(),uri);

        //generate new mqtt client
        String clientId = MqttClient.generateClientId();
        client = new MqttAndroidClient(this.getApplicationContext(), MQTTHOST, clientId);

        options = new MqttConnectOptions();
        options.setUserName(USERNAME);
        options.setPassword(PASSWORD.toCharArray());


        try {
            IMqttToken token = client.connect(options);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                //generate toast object to display successful connection
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"Device Connected",Toast.LENGTH_SHORT).show();
                    setSubscription();
                }

                @Override
                //generate toast object to display unsuccessful connection
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"connection failed!",Toast.LENGTH_SHORT).show();
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }

       client.setCallback(new MqttCallback() {
           @Override
           //if connection lost
           public void connectionLost(Throwable cause) {
            //do nothing
           }
           //when a message arrives to subscription topic
           @Override
           public void messageArrived(String topic, MqttMessage message) throws Exception {
               String payload=new String(message.getPayload());
               //JSON format object received
               //payload is converted from json form to string
               //the field sample of the json format contains the bingo number
               JSONObject jsonpayload=new JSONObject(payload);
               subText.setText(jsonpayload.getString("Sample"));

               //vibration of phone when number received
               vibrator.vibrate(500);
               // myRingtone.play();
               //text to speech function implemented to output the number
               // and the corresponding quote as speech
               speak();


           }

           @Override
           //function that runs when message is received
           public void deliveryComplete(IMqttDeliveryToken token) {
            //do nothing
           }
       });



    }



    //this is the message sent by the button BINGO
    public void pub(View v){
        String topic = topic_stream_publish;
        //sends a json format message to topic
        String message = "{"+'"'+"bingo"+'"'+":"+'"'+"1"+'"'+"}";
        byte[] encodedPayload = new byte[0];
        try {
            //publishes the message to MQTT broker, qos set to 0
            client.publish(topic, message.getBytes(),0,false);
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }


    //establishes subscription and QoS
    private void setSubscription(){
        try{
            client.subscribe(topic_stream_subscribe,0);
        }catch (MqttException e){
            e.printStackTrace();
        }
    }

    //connect to the broker
    public void conn(View v){
        try {
            IMqttToken token = client.connect(options);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                //generate toast object to display successful connection
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"Device Connected",Toast.LENGTH_SHORT).show();
                    setSubscription();
                }

                @Override
                //generate toast object to display unsuccessful connectio,
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"connection failed!",Toast.LENGTH_SHORT).show();
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    //disconnect to the broker
    public void disconn(View v){
        try {
            IMqttToken token = client.disconnect();
            token.setActionCallback(new IMqttActionListener() {
                @Override
                //generate toast object to display successful disconnection
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"Device Disconnected!",Toast.LENGTH_SHORT).show();
                }
                //generate toast object to display unsuccessful disconnection
                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"Disconnection failed!",Toast.LENGTH_SHORT).show();
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    //text to speech function
    public void speak() throws JSONException {
        //stores the number of the corresponding textview to variable message
        TextView newtext=(TextView)findViewById(R.id.subText);
        message=newtext.getText().toString();


        messagespeech=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status!=TextToSpeech.ERROR){
                    //set language of voice
                    messagespeech.setLanguage(Locale.UK);

                    //arra y that stores quote for each number
                    String BingoNames[]={"Kelly’s Eye", "One Little Duck " , "Cup of Tea " , "Knock at the Door " , "Man Alive " ,
                            "Tom Mix " , "Lucky Seven " , "Garden Gate " , "Doctor’s Orders " , "Cameron’s Den " , "Legs 11 " ,
                            "One Dozen " , "Unlucky for Some " , "Valentine’s Day " , "Young and Keen " , "Sweet 16 " , "Dancing Queen " , "Coming of Age " , "Goodbye Teens " , "One Score " , "Royal Salute " ,
                            "Two Little Ducks " , "Thee and Me " , "Two Dozen " , "Duck and Dive " , "Pick and Mix " , "Gateway to Heaven " ,
                            "Over Weight " , "Rise and Shine " , "Dirty Gertie " , "Get Up and Run " , "Buckle My Shoe " , "Dirty Knee " ,
                            "Ask for More " , "Jump and Jive " , "Three Dozen " , "More than 11 " , "Christmas Cake " , "Steps " , "Naughty 40 " ,
                            "Time for Fun " , "Winnie the Pooh " , "Down on Your Knees " , "Droopy Drawers " , "Halfway There " , "Up to Tricks " , "Four and Seven " , "Four Dozen " , "PC " ,
                            "Half a Century " , "Tweak of the Thumb " , "Danny La Rue " , "Stuck in the Tree " , "Clean the Floor " , "Snakes Alive " , "Was She Worth It? " , "Heinz Varieties " ,
                            "Make Them Wait " , "Brighton Line " , "Five Dozen " , "Bakers Bun " , "Turn the Screw " , "Tickle Me 63 " , "Red Raw " , "Old Age Pension " , "Clickety Click " ,
                            "Made in Heaven " , "Saving Grace " , "Either Way Up " , "Three Score and 10 " , "Bang on the Drum " , "Six Dozen " , "Queen B " , "Candy Store " , "Strive and Strive " , "Trombones " , "Sunset Strip " , "Heaven’s Gate " ,
                            "One More Time " , "Eight and Blank " , "Stop and Run " , "Straight On Through " , "Time for Tea " , "Seven Dozen " , "Staying Alive " , "Between the Sticks " , "Torquay in Devon " , "Two Fat Ladies " , "Nearly There " , "Top of the Shop"};
                    //variable int stores number
                    int in = Integer.valueOf(message.toString());
                    String toSpeak=BingoNames[in-1]+" ..   Number  "+ message;
                    //generate toast object to display quote and number
                    Toast.makeText(getApplicationContext(),toSpeak,Toast.LENGTH_SHORT).show();
                    messagespeech.speak(toSpeak,TextToSpeech.QUEUE_FLUSH,null);

                }
            }
        });


    };



}
